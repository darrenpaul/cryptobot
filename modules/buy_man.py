import time
from . import bitstamp
from mongo_manager import mongo_man
'''
Runs every X seconds
Gets the latest price from exchange
Then adds the latest price to database
'''

class Buyer:
    def __init__(self, interval=3600, currency_pairs=['btceur'], dry_run=False):
        self.interval = interval
        self.currency_pairs = currency_pairs
        self.dry_run = dry_run

    def start_buyer(self):
        while True:
            for pair in self.currency_pairs:
                # get latest price from database
                latest_price = bitstamp.get_latest_ticker(pair)
                # add latest price to database
                if not self.dry_run:
                    pass
                else:
                    print(latest_price)
                time.sleep(self.interval)
