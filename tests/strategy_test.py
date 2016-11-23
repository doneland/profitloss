from unittest import TestCase
from datetime import datetime

from strategy import Strategy
from price import Price


class TestStrategy(TestCase):

    def setUp(self):
        pass

    def test_strategy_instance(self):
        s = Strategy(start_amount=1000, sl=0.02, tpmulti=2)

        # Check whether basic properties where set correctly.
        self.assertEqual(s.options['start_amount'], 1000)
        self.assertEqual(s.options['stop_loss'], 0.02)
        self.assertEqual(s.options['tpmulti'], 2)
        self.assertEqual(s.options['transaction_size'], 10)
        self.assertEqual(s.options['max_open_positions'], 10)

        # Statistics properties are set to zero.
        self.assertEqual(s.stats['trades_count'], 0)
        self.assertEqual(s.stats['positive_count'], 0)
        self.assertEqual(s.stats['negative_count'], 0)
        self.assertEqual(s.stats['balance_highest'], 0)
        self.assertEqual(s.stats['balance_lowest'], 0)
        self.assertEqual(s.stats['positive_max_in_row'], 0)
        self.assertEqual(s.stats['negative_max_in_row'], 0)

        # Properties in status.
        self.assertEqual(s.status['remaining_amount'],
                         s.options['start_amount'])
        self.assertEqual(s.status['open_trades_count'], 0)
        self.assertEqual(s.status['closed_trades_count'], 0)

        # Property that cache trades made. At the beginning this
        # property should be empty.
        self.assertEqual(s.trades, [])

    def test_stream_price(self):
        s = Strategy(start_amount=1000, sl=0.02, tpmulti=2)
        p1 = Price([datetime(2015, 12, 31, 12, 00), 10])
        s.stream_price(p1)

        self.assertEqual(len(s.trades), 1)
        # Remaining amount comes by subtracting first transaction total amount.
        self.assertEqual(s.status['remaining_amount'], 900)
        self.assertEqual(s.status['open_trades_count'], 1)

        trx1 = s.trades[0]
        self.assertEqual(trx1.get('entry_amount'), 100)
        self.assertEqual(trx1.get('stop_loss_price'), 8)
        self.assertEqual(trx1.get('take_profit_price'), 14)

        # Balance count should be equal to transactions count.
        self.assertEqual(len(s.balances), len(s.trades))

        ##
        # Add second price tick.
        ##
        p2 = Price([datetime(2015, 12, 31, 12, 30), 12])
        s.stream_price(p2)

        # Remaining amount comes by subtracting first transaction total amount.
        self.assertEqual(s.status['remaining_amount'], 780)
        self.assertEqual(s.status['open_trades_count'], 2)

        # Last record of balance should be updated.
        self.assertEqual(s.current_price.get('value'), 12)
        self.assertEqual(len(s.balances), len(s.trades))
        self.assertEqual(s.balances[-1], 1020)

        ##
        # Add third price
        ##
        p3 = Price([datetime(2015, 12, 31, 13, 00), 14])
        s.stream_price(p3)

        # Remaining amount comes by subtracting first transaction total amount.
        self.assertEqual(s.status['remaining_amount'], 780)
        self.assertEqual(s.status['open_trades_count'], 2)
        self.assertEqual(s.status['closed_trades_count'], 1)

        # Last record of balance should be updated.
        self.assertEqual(s.current_price.get('value'), 14)
        self.assertEqual(len(s.balances), len(s.trades))
        self.assertEqual(s.balances[-1], 1060)
