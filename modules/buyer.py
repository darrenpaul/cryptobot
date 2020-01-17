import time
from pprint import pprint
from . import bitstamp
from . import thread_man
from . import general_utils as gutils
from . import math_utils
from .mongo_manager import mongo_man
'''
Runs every X seconds
Gets the latest price from exchange
Then adds the latest price to database
'''


DATA = [
    {"volume": "1514.19349025", "last": "7839.12", "timestamp": "1579216197",
     "bid": "7827.08", "vwap": "7786.06", "high": "7940.57", "low": "7700.00", "ask": "7838.74", "open": "7913.90"},
    {"volume": "1514.19448869", "last": "7839.22", "timestamp": "1579216534",
     "bid": "7832.15", "vwap": "7786.00", "high": "7940.00", "low": "7700.00", "ask": "7839.22", "open": "7913.90"},
    {"volume": "1513.10943252", "last": "7839.22", "timestamp": "1579216649",
     "bid": "7833.90", "vwap": "7785.90", "high": "7940.00", "low": "7700.00", "ask": "7839.22", "open": "7913.90"},
    {"volume": "1509.71594900", "last": "7836.89", "timestamp": "1579217056",
     "bid": "7830.00", "vwap": "7785.60", "high": "7940.00", "low": "7700.00", "ask": "7836.57", "open": "7913.90"},
    {"volume": "1506.17279357", "last": "7836.23", "timestamp": "1579217382",
     "bid": "7825.97", "vwap": "7785.27", "high": "7940.00", "low": "7700.00", "ask": "7836.23", "open": "7913.90"},
    {"volume": "1501.71110885", "last": "7834.02", "timestamp": "1579217622",
     "bid": "7824.45", "vwap": "7784.85", "high": "7940.00", "low": "7700.00", "ask": "7834.90", "open": "7913.90"},
    {"volume": "1459.96090170", "last": "7792.34", "timestamp": "1579221223",
     "bid": "7792.34", "vwap": "7781.67", "high": "7868.71", "low": "7700.00", "ask": "7806.78", "open": "7826.89"},
    {"volume": "1415.90205122", "last": "7791.73", "timestamp": "1579224824",
     "bid": "7796.88", "vwap": "7781.46", "high": "7868.71", "low": "7700.00", "ask": "7809.34", "open": "7826.89"},
    {"volume": "1369.41247119", "last": "7841.24", "timestamp": "1579228427",
     "bid": "7833.36", "vwap": "7783.08", "high": "7868.71", "low": "7700.00", "ask": "7839.20", "open": "7826.89"},
    {"volume": "1365.73997330", "last": "7924.45", "timestamp": "1579232027",
     "bid": "7903.11", "vwap": "7785.85", "high": "7924.45", "low": "7702.81", "ask": "7916.54", "open": "7826.89"},
    {"volume": "1349.44201865", "last": "7862.98", "timestamp": "1579235629",
     "bid": "7862.96", "vwap": "7786.87", "high": "7924.45", "low": "7702.81", "ask": "7873.00", "open": "7826.89"},
    {"volume": "1335.80571889", "last": "7952.57", "timestamp": "1579239231",
     "bid": "7940.00", "vwap": "7788.30", "high": "7955.66", "low": "7702.81", "ask": "7950.11", "open": "7826.89"},
    {"volume": "1426.19552631", "last": "8048.92", "timestamp": "1579242833",
     "bid": "8043.39", "vwap": "7808.83", "high": "8075.40", "low": "7702.81", "ask": "8047.85", "open": "7826.89"},
    {"volume": "1465.42105419", "last": "7998.09", "timestamp": "1579246433",
     "bid": "8005.28", "vwap": "7821.49", "high": "8075.40", "low": "7702.81", "ask": "8015.00", "open": "7826.89"},
    {"volume": "1570.90681903", "last": "8026.20", "timestamp": "1579250036",
     "bid": "8020.00", "vwap": "7841.73", "high": "8077.56", "low": "7702.81", "ask": "8027.07", "open": "7826.89"},
    {"volume": "1621.94062664", "last": "8052.13", "timestamp": "1579253636",
     "bid": "8041.62", "vwap": "7858.14", "high": "8077.56", "low": "7702.81", "ask": "8052.01", "open": "7826.89"},
    {"volume": "1780.49255922", "last": "8012.75", "timestamp": "1579257237",
     "bid": "7997.38", "vwap": "7889.54", "high": "8108.88", "low": "7724.72", "ask": "8012.73", "open": "7826.89"},
    {"volume": "1821.78350571", "last": "8042.78", "timestamp": "1579260839",
     "bid": "8030.31", "vwap": "7900.54", "high": "8108.88", "low": "7729.05", "ask": "8042.12", "open": "7826.89"},
    {"volume": "1865.18095398", "last": "7964.06", "timestamp": "1579264436",
     "bid": "7946.11", "vwap": "7910.30", "high": "8108.88", "low": "7729.05", "ask": "7963.37", "open": "7826.89"},
    {"volume": "1919.40523058", "last": "7977.98", "timestamp": "1579268038",
     "bid": "7966.00", "vwap": "7917.05", "high": "8108.88", "low": "7729.05", "ask": "7977.67", "open": "7826.89"},
]


class Buyer:
    def __init__(self, interval=3600, currency_pairs=['btceur'], dry_run=False):
        self.interval = interval
        self.currency_pairs = currency_pairs
        self.dry_run = dry_run

    def start_buyer(self):
        thread = thread_man.ThreadManager()
        thread.spawn_new_thread('buyer', self.__buyer, **{})

    def __buyer(self):
        funds = bitstamp.get_account_funds()
        buy_price = 0
        volume = 0
        while True:
            if funds == 0:
                funds = self.__seller(volume, buy_price)
            for pair in self.currency_pairs:
                price_data = gutils.get_only_key_values(DATA, 'last')
                current_price = price_data[-1]
                main_mean = math_utils.get_mean(price_data[10:])
                tri_mean = math_utils.get_mean(price_data[3:])
                volume = float(funds)/float(tri_mean)
                buy_price = tri_mean
                print('bought')
                # if current price < main mean
                # if not current
                if not self.dry_run:
                    pass
                else:
                    pass
                time.sleep(self.interval)

    def __seller(self, volume, buy_price):
        if volume == 0:
            return 100
        price_data = gutils.get_only_key_values(DATA, 'last')
        current_price = price_data[-1]
        main_mean = math_utils.get_mean(price_data[10:])
        tri_mean = math_utils.get_mean(price_data[3:])
        print(current_price)
        print(main_mean)
        print(tri_mean)
        print buy_price

        buy_price = math_utils.get_percentage_increase(buy_price, 2.5)
        if buy_price > tri_mean:
            print('sold'
            return volume * main_mean
