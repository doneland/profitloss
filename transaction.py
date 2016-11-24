
from price import Price

class Transaction(object):

    def __init__(self, data):
        self.data = {
            'type': data['type'],
            'entry_price': data['entry_price'],
            'quantity': data['quantity'],
            'entry_date': data['entry_date'],
            'entry_amount': 0,
            'leverage': data['leverage'],
            'sl_amount': data['sl_amount'],
            'tp_amount': data['tp_amount'], 

            # Fields are calculated from data privided.
            'stop_loss_price': 0,
            'take_profit_price': 0,

            # Fields that is set when transaction is closed.
            'closed': False,
            'close_price': None,
            'close_date': None,
            'close_reason': None,
            'close_pl': 0,
            'close_amount': 0,
        }

        # Calculate enter amount of transaction.
        self.calc_enter_amount()
        # Calculate take profit and stop loss prices.
        self.calc_tp_sl()

    def calc_enter_amount(self):
        p = self.get('entry_price')
        q = self.get('quantity')
        self.set('entry_amount', (p * q))

    def calc_tp_sl(self):
        ttype = self.get('type')
        p = self.get('entry_price')
        q = self.get('quantity')
        sla = self.get('sl_amount')
        tpa = self.get('tp_amount')

        if ttype == 'BUY':
            slprice = p - (sla/q)
            tpprice = p + (tpa/q)
            self.set('stop_loss_price', slprice) 
            self.set('take_profit_price', tpprice) 
        elif ttype == 'SELL':
            slprice = p + (sla/q)
            tpprice = p - (tpa/q)
            self.set('stop_loss_price', slprice) 
            self.set('take_profit_price', tpprice)

    def get_pl(self, price):
        q = self.get('quantity')
        ep = self.get('entry_price')
        cp = price.get('value')
        pl = (cp * q) - (ep * q)
        return pl

    def close(self, price, reason):
        self.set('closed', True)
        self.set('close_price', price.get('value'))
        self.set('close_date', price.get('date'))
        self.set('close_reason', reason)
        self.set('close_pl', self.get_pl(price))
        self.set('close_amount', price.get('value') * self.get('quantity'))

    def check_sl_tp(self, price):
        """ 
        Checks and validate transaction. If price reached stop loss or take profit
        limits, close the transaction.
        """
        p = price.get('value')
        d = price.get('date')
        sl = self.get('stop_loss_price')
        tp = self.get('take_profit_price')
        ttype = self.get('type')

        if ttype == 'BUY':
            if sl >= p:
                sell_price = Price([d, sl])
                self.close(sell_price, 'SL')
            elif tp <= p:
                sell_price = Price([d, tp])
                self.close(sell_price, 'TP')

        if ttype == 'SELL':
            if sl <= p:
                sell_price = Price([d, sl])
                self.close(sell_price, 'SL')
            elif tp >= p:
                sell_price = Price([d, tp])
                self.close(sell_price, 'TP')

    def get(self, field):
        return self.data[field]

    def set(self, field, value):
        self.data[field] = value
