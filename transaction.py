

class Transaction(object):

    def __init__(self, data):
        self.data = {
            'type': data['type'],
            'entry_price': data['entry_price'],
            'stop_loss_price': data['stop_loss_price'],
            'take_profit_price': data['take_profit_price'],
            'quantity': data['quantity'],
            'entry_date': data['entry_date'],
            'entry_amount': 0,

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

    def calc_enter_amount(self):
        p = self.get('entry_price')
        q = self.get('quantity')
        self.set('entry_amount', (p * q))

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

    def get(self, field):
        return self.data[field]

    def set(self, field, value):
        self.data[field] = value
