"""  Contains Strategy class. """
from datetime import datetime
from datetime import timedelta

from transaction import Transaction


class Strategy(object):

    def __init__(self, start_amount, sl=0.01, tpmulti=2):
        self.options = {
            'start_amount': start_amount,
            'stop_loss': sl,
            'tpmulti': tpmulti,
            'transaction_size': 10,
            'max_open_positions': 10
        }

        self.stats = {
            'trades_count': 0,
            'positive_count': 0,
            'negative_count': 0,
            'balance_highest': 0,
            'balance_lowest': 0,
            'positive_max_in_row': 0,
            'negative_max_in_row': 0
        }

        self.status = {
            'remaining_amount': self.options['start_amount'],
            'open_trades_count': 0,
            'closed_trades_count': 0,
        }

        # All trades
        self.trades = []
        # Balances
        self.balances = []
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
        self.calc_balance()

    def close_strategy(self, trade, price):
        """
        Check and close trades that reached stop loss or take profit values. 
        """
        sl = trade.get('stop_loss_price')
        tp = trade.get('take_profit_price')
        trx_type = trade.get('type')

        if trx_type == 'BUY':
            if sl >= price.get('value'):
                trade.close(price, 'SL')
            elif tp <= price.get('value'):
                trade.close(price, 'TP')

        if trx_type == 'SELL':
            if sl <= price.get('value'):
                trade.close(price, 'SL')
            elif tp >= price.get('value'):
                trade.close(price, 'TP')

    def enter_strategy(self, price):
        """
        Makes entry transaction.
        """
        trx_size = self.options['transaction_size']
        trx_amount = price.get('value') * trx_size
        stop_loss_diff = (self.options['stop_loss']
                          * self.options['start_amount']) / trx_size
        take_profit_diff = stop_loss_diff * self.options['tpmulti']

        # If transaction value is larger than remaining amount in portfolio,
        # don't do any trades.
        if trx_amount > self.status['remaining_amount']:
            return

        # TODO: Add restriction for open positions.
        trx = Transaction({
            'type': 'BUY',
            'entry_price': price.get('value'),
            'stop_loss_price': price.get('value') - stop_loss_diff,
            'take_profit_price': price.get('value') + take_profit_diff,
            'quantity': trx_size,
            'entry_date': price.get('date')
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
        self.calc_status()

    def calc_stats(self):
        self.stats['trades_count'] = len(self.trades)
        return self.stats

    def calc_balance(self):
        balance = self.options['start_amount']
        for t in self.trades:
            if t.get('closed') == False:
                balance += t.get_pl(self.current_price)
            else:
                balance += t.get('close_pl')
        self.balances.append(balance)

    def calc_status(self):
        # Remaining amount shows how much remain money for the next trade.
        remaining_amount = self.options['start_amount']
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
