from math import fabs
import os
import time

from pathlib import Path
from datetime import datetime
from modules import luno, file_reader, mathematics, logger
from classes import buy_manager, sell_manager, price_manager, trend_manager


FACTOR = 10 ** 2
PROCESS_TIMER = 300


class AlgoBot(
    buy_manager.BuyManager,
    sell_manager.SellManager,
    price_manager.PriceManager,
    trend_manager.TrendManager,
    logger.BotLogger):

    def __init__(self, dry_run=True):
        buy_manager.BuyManager.__init__(self)
        sell_manager.SellManager.__init__(self)
        price_manager.PriceManager.__init__(self)
        trend_manager.TrendManager.__init__(self)
        logger.BotLogger.__init__(self)

        self.dry_run = dry_run

        self.trading_pair = 'XBTZAR'
        self.profit_margin = 2
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

        self.logger_message = ['']

    def save_pending_order(self, data, order_type):
        file_reader.write_data({'orders': data}, f'pending_orders_{order_type}')

    def get_pending_orders(self, order_type):
        data = file_reader.read_data(f'pending_orders_{order_type}')
        return data.get('orders') or []

    def process_pending_orders(self, pending_orders, order_type):
        incomplete_orders = []
        complete_orders = []
        for i in pending_orders:
            order = luno.get_order(i['order_id'])
            if order.get('state') == 'COMPLETE':
                complete_orders.append({**i, **order})
            else:
                incomplete_orders.append({**i, **order})

        pending_orders = incomplete_orders
        self.save_pending_order(pending_orders, order_type)
        return {'pending': pending_orders, 'complete': complete_orders}

    def run(self):
        has_data = False
        did_buy = False

        self.logger_message = ['']

        self.logger_message.append(f'CURRENT FUNDS: {float(luno.getSpendableBalance())}')

        current_price = self.get_current_price()
        self.logger_message.append(f'CURRENT PRICE: {current_price}')

        if len(self.past_prices) > self.trend_size:
            has_data = True

        if has_data:
            self.logger_message.append(f'cancelling open orders...')
            cancelled_orders = luno.close_open_orders(self.trading_pair)
            if len(cancelled_orders) > 0:
                self.pending_orders = []
                self.logger_message.append(f'cancelled open orders {cancelled_orders}')

            self.update_trend(current_price)

            average_buy_price = self.get_buy_price_average()
            self.logger_message.append(f'AVERAGE BUY PRICE: {average_buy_price}')

            # BUY ORDER
            if self.trend <= self.trend_margin:
                if self.trend >= self.min_trend_margin:
                    self.process_buy_order(current_price)
                    did_buy = True

            if did_buy is False:
                if len(self.bought_orders) > 0:
                    if float(average_buy_price) < float(current_price):
                        self.process_sell_order(average_buy_price)

        self.log_info_message(self.logger_message)

    def get_profit_sell_price(self, average_buy_price):
        return mathematics.get_percentage(average_buy_price, self.profit_margin) + average_buy_price


if __name__ == "__main__":
    bot = AlgoBot(dry_run=False)

    bot.log_info('Running AlgoBot...')

    bot.get_config()
    bot.get_past_prices()
    bot.pending_orders_buy = bot.get_pending_orders('buy')
    bot.pending_orders_sell = bot.get_pending_orders('sell')
    bot.get_buy_orders()
    bot.get_completed_buy_orders()
    bot.get_sell_orders()
    bot.get_past_trends()

    count = PROCESS_TIMER
    while True:
        bot.get_config()

        if count % 10 == 0:
            orders = bot.process_pending_orders(bot.pending_orders_buy, 'buy')
            bot.bought_orders += orders['complete']
            bot.pending_orders_buy = orders['pending']
            bot.save_buy_order()

            orders = bot.process_pending_orders(bot.pending_orders_sell, 'sell')
            clear_buy_orders = False
            if(len(orders['complete']) > 0):
                clear_buy_orders = True
            bot.sell_orders += orders['complete']
            bot.pending_orders_sell = orders['pending']
            bot.save_sell_order(clear_buy_orders)

        if count >= PROCESS_TIMER:
            bot.run()
            count = 0

        time.sleep(1)
        count += 1
