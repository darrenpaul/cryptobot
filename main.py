from modules import collector
from modules.mongo_manager import mongo_man

currency_pair = 'btceur'

# get latest price
latest_price = collector.latest_ticker(currency_pair)
print(latest_price)
# add latest price to database
# db = mongo_man.Mongo('crypto', currency_pair)
# db.add_single(latest_price)
# get latest 10 entries in database

# get average of last price from database entries

# check if can sell

# check if can buy
