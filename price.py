"""module: contains price class."""


class Price(object):

    def __init__(self, price):
        self.data = {
            'date': price[0],
            'value': price[1],
        }

    def get(self, field):
        return self.data[field]
