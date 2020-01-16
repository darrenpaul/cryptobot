import time
from modules import collector
from modules.mongo_manager import mongo_man

INTERVALS = 3600
currency_pair = 'btceur'

while True:
    # get latest price
    latest_price = collector.latest_ticker(currency_pair)
    print(latest_price)
    # add latest price to database
    db = mongo_man.Mongo('crypto', currency_pair)
    db.add_single(latest_price)
    # get latest 10 entries in database

    # get average of last price from database entries

    # check if can sell

    # check if can buy
    time.sleep(INTERVALS)
