import os
import time

from pathlib import Path
from datetime import datetime
from modules import luno, file_reader, mathematics
from classes import buy_manager, sell_manager, price_manager

FACTOR = 10 ** 2


class AlgoBot(buy_manager.BuyManager, sell_manager.SellManager, price_manager.PriceManager):
    def __init__(self, dry_run=True):
        buy_manager.BuyManager.__init__(self)
        sell_manager.SellManager.__init__(self)
        price_manager.PriceManager.__init__(self)

        self.dry_run = dry_run

        self.trading_pair = 'XBTZAR'
        self.profit_margin = 2
        self.trend_size = 10
        self.trend_margin = 100
        self.min_trend_margin = 90
        self.purchase_percentage = 5
        self.funds = float(luno.getSpendableBalance())

    def get_config(self):
        file_path = os.path.join(Path(__file__).parent, 'config.yml')
        config = file_reader.read_yaml(file_path)
        self.trading_pair = f'{config["coin"]}{config["currency"]}'
        self.profit_margin = config['profitMargin']
        self.trend_size = config['trendSize']
        self.trend_margin = config['trendMargin']
        self.min_trend_margin = config['minTrendMargin']
        self.purchase_percentage = config['purchasePercent']
        self.min_trade_amount = config['minTradeAmount'][config['coin']]

    def run(self):
        print('=== Running AlgoBot... ============')
        print(f'Current time: {datetime.now().strftime("%H:%M:%S")}')
        print(f'Current date: {datetime.now().strftime("%d-%b-%Y")}')
        print('='*40)

        print('Cancelling open orders...')
        cancelled_orders = luno.close_open_orders(self.trading_pair)
        if len(cancelled_orders) > 0:
            self.pending_orders = []
            print('Cancelled open orders', cancelled_orders)

        current_price = self.get_current_price()

        if len(self.past_prices) < self.trend_size:
            return

        trend = mathematics.get_trend(self.past_prices, self.trend_size, int(self.trend_size / 2))
        print(f'Trend: {trend}')

        average_buy_price = self.get_buy_price_average()
        print(f'Average Buy Price: {average_buy_price}')

        # BUY ORDER
        if trend <= self.trend_margin:
            if trend >= self.min_trend_margin:
                self.process_buy_order(current_price)
                return

        if len(self.bought_orders) == 0:
            return

        if float(average_buy_price) < float(current_price):
            self.process_sell_order(current_price, average_buy_price)

    def get_profit_sell_price(self, average_buy_price):
        return mathematics.get_percentage(average_buy_price, self.profit_margin) + average_buy_price


if __name__ == "__main__":
    bot = AlgoBot(dry_run=False)
    bot.get_config()
    bot.get_past_prices()
    bot.get_pendings_orders()
    bot.get_buy_orders()
    bot.get_sell_orders()

    count = 300
    while True:
        bot.get_config()

        if count >= 300:
            bot.run()
            count = 0

        if count % 5 == 0:
            bot.process_pending_orders()

        time.sleep(1)

        count += 1
