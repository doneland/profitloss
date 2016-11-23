"""  Contains Strategy class. """
from datetime import datetime
from datetime import timedelta

class Strategy(object):

    def __init__(self, start_amount, sl=0.01, tpmulti=2):
        self.options = {
            'start_amount': 10000,
            'sl': sl,
            'tpmulti': tpmulti,
            'transaction_size': 10,
            'max_open': 10
        }

        self.stats = {
            'trades_count': 0,
            'profitable_count': 0,
            'loss_count': 0,
            'amount_highest': 0,
            'amount_lowest': 0,
            'max_in_row_profit': 0,
            'max_in_row_loss': 0
        }

        self.status = {
            'current_value': self.options['start_amount'],
            'open_trades_count': 0
        }

        # All trades
        self.trades = []
        # All amount values during the trading period.
        self.amounts = []

    def stream_price(self, price): 
        """
        Stream price. Go through each trade in self.trades and provide this price.
        Trade should know from the price whether it should be closed or left without 
        changes.
        """
        for trade in self.trades:
            if trade.get('closed') == False:
                self.close_strategy(trade, price)
        
        # Update parameters of strategy.
        self.update()
        # Check enter strategy.
        self.enter_strategy(price)
        

    def close_strategy(self, trade, price):
        """
        Check validity of trade according price provided.
        """
        sl = trade.get('stop_loss_price')
        tp = trade.get('take_profit_price')
        trx_type = trade.get('type')

        if trx_type == 'BUY':
            if sl >= price.get('value'):
                trade.close(price)
            elif tp <= price.get('value'):
                trade.close(price)
        
        if trx_type == 'SELL':
            if sl <= price.get('value'):
                trade.close(price)
            elif tp >= price.get('value'):
                trade.close(price)


    def enter_strategy(self, price):
        """
        Makes entry transaction.
        """
        trx_size = self.options['transaction_size']
        trx_amount = price.get('value') * trx_size
        stop_loss_diff = (self.options['stop_loss'] * self.options['start_amount']) / trx_size
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
                'create_date': price.get('date') - timedelta(minutes=30)
            })

        # Add transaction
        self.add_trade(trx)
        # Update all the props and statistics.
        self.update()

    def add_trade(self, transaction):
        """
        Add transaction as trade in self.trade.
        """
        self.trades.append(transaction)
        self.update()

    def update(self):
        """
        Method updates status, statistics and etc.
        """
        self.calc_stats()
        self.update_state()

    def calc_stats(self):
        pass

    def update_state(self):
        remaining_amount = self.options['start_amount']
        total_amount = self.options['start_amount']

        for t in self.trades:
            if t.get('closed') == False:
                remaining_amount -= t.get('enter_amount')
                total_amount += t.change(price)
                self.amounts.append(remaining_amount)
            else: 
                remaining_amount += t.get('close_amount')
                self.amounts.append(remaining_amount)

        self.status['remaining_amount'] = remaining_amount





        