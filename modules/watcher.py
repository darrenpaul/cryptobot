import time
from . import bitstamp
from mongo_manager import mongo_man
'''
Runs every X seconds
Gets the latest price from exchange
Then adds the latest price to database
'''

class Watcher:
    def __init__(self, interval=3600, currency_pairs=['btceur'], dry_run=False):
        self.interval = interval
        self.currency_pairs = currency_pairs
        self.dry_run = dry_run

    def start_watcher(self):
        while True:
            for pair in self.currency_pairs:
                # get latest price
                latest_price = bitstamp.get_latest_ticker(pair)
                # add latest price to database
                if not self.dry_run:
                    db = mongo_man.Mongo('crypto', pair)
                    db.add_single(latest_price)
                    print('price added to database')
                else:
                    print(latest_price)
                time.sleep(self.interval)
