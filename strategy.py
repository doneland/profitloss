"""  Contains Strategy class. """
from datetime import datetime
from datetime import timedelta
import numpy as np

from transaction import Transaction


class Strategy(object):

    def __init__(self, start_amount, sl=0.01, tpmulti=2, leverage=1, transaction_size=10):
        self.options = {
            'start_amount': start_amount,
            'stop_loss': sl,
            'tpmulti': tpmulti,
            'transaction_size': transaction_size,
            'max_open_positions': 10,
            'leverage': leverage
        }

        self.stats = {
            'last_balance': 0,
            'trades_count': 0,
            'positive_count': 0,
            'negative_count': 0,
            'balance_highest': 0,
            'balance_lowest': 0,
            'positive_max_in_row': 0,
            'negative_max_in_row': 0
        }

        self.status = {
            # Remaining amount with leverage.
            'remaining_amount': (self.options['start_amount'] * self.options['leverage']),
            'open_trades_count': 0,
            'closed_trades_count': 0,
        }

        # All trades
        self.trades = []
        # Balances
        self.balances = []
        self.balances_columns = ['date', 'balance']
        # Current price.
        self.current_price = None

    def stream_price(self, price):
        """
        Stream price. Go through each trade in self.trades and provide this price.
        Trade should know from the price whether it should be closed or left without 
        changes.
        """

        # Cache current price.
        self.current_price = price

        # Adopt closing strategies for open trades in the book.
        for trade in self.trades:
            if trade.get('closed') == False:
                self.close_strategy(trade, price)

        # Check enter strategy.
        self.enter_strategy(price)

        # Update parameters of strategy.
        self.update()
        

    def close_strategy(self, trade, price):
        """
        Check and close trades that reached stop loss or take profit values. 
        """
        trade.check_sl_tp(price)


    def enter_strategy(self, price):
        """
        Makes entry transaction.
        """
        trx_size = self.options['transaction_size']
        trx_amount = price.get('value') * trx_size
        sl_amount = (self.options['stop_loss'] * self.options['start_amount'])
        tp_amount = sl_amount * self.options['tpmulti']
        leverage = self.options['leverage']
        remaining = self.status['remaining_amount']

        # If transaction value is larger than remaining amount in portfolio,
        # don't do any trades.
        if trx_amount > remaining:
            return

        # TODO: Add restriction for open positions.
        trx = Transaction({
            'type': 'BUY',
            'entry_price': price.get('value'),
            'sl_amount': sl_amount,
            'tp_amount': tp_amount,
            'quantity': trx_size,
            'entry_date': price.get('date'),
            'leverage': leverage,
        })

        # Add transaction
        self.add_trade(trx)

    def add_trade(self, transaction):
        """
        Add transaction as trade in self.trade.
        """
        self.trades.append(transaction)

    def update(self):
        """
        Method updates status, statistics and etc.
        """
        self.calc_balance()
        self.calc_status()
        self.calc_stats()

    def calc_stats(self):
        positive_count = 0
        negative_count = 0
        in_row_positive = 0
        max_in_row_positive = 0
        in_row_negative = 0
        max_in_row_negative = 0
        for t in self.trades:
            if t.get('closed') == True:
                # Calculate positive count
                if t.get('close_pl') > 0:
                    positive_count += 1
                    in_row_positive += 1
                    if positive_count > max_in_row_positive:
                        max_in_row_positive = in_row_positive
                    in_row_negative = 0
                elif t.get('close_pl') < 0:
                    negative_count += 1
                    in_row_negative += 1
                    in_row_positive = 0
                    if in_row_negative > max_in_row_negative:
                        max_in_row_negative = in_row_negative
            else:
                pass

        balances = np.array([b[1] for b in self.balances])
        if balances.size != 0:
            self.stats['balance_highest'] = balances.max()
            self.stats['balance_lowest'] = balances.min()
            self.stats['last_balance'] = balances[-1]

        self.stats['trades_count'] = len(self.trades)
        self.stats['positive_count'] = positive_count
        self.stats['negative_count'] = negative_count
        self.stats['positive_max_in_row'] = max_in_row_positive
        self.stats['negative_max_in_row'] = max_in_row_negative

    def calc_balance(self):
        balance = self.options['start_amount']
        for t in self.trades:
            if t.get('closed') == False:
                balance += t.get_pl(self.current_price)
            else:
                balance += t.get('close_pl')
        # Create array with date and value of balance. 
        balance_record = [self.current_price.get('date'), balance]
        self.balances.append(balance_record)

    def calc_status(self):
        # Remaining amount shows how much remain money for the next trade.
        leverage = self.options['leverage']
        remaining_amount = self.options['start_amount'] * leverage
        open_trades = 0
        closed_trades = 0
        for t in self.trades:
            if t.get('closed') == False:
                remaining_amount -= t.get('entry_amount')
                open_trades += 1
            else:
                closed_trades += 1
                remaining_amount += t.get('close_pl')
        self.status['remaining_amount'] = remaining_amount
        self.status['open_trades_count'] = open_trades
        self.status['closed_trades_count'] = closed_trades