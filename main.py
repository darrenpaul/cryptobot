import os
from pprint import pprint
import time
import math

from pathlib import Path
from modules import luno, file_reader, mathematics, logger
from classes import buy_manager, sell_manager, order_manager, price_manager, trend_manager, config_manager, funds_manager


FACTOR = 10 ** 2
PROCESS_TIMER = 300

# True
DRY_RUN = False
CAN_BUY = True
CAN_SELL = True


class AlgoBot(
    buy_manager.BuyManager,
    sell_manager.SellManager,
    order_manager.OrderManager,
    price_manager.PriceManager,
    trend_manager.TrendManager,
    logger.BotLogger,
    config_manager.ConfigManager,
    funds_manager.FundsManager):

    def __init__(self):

        buy_manager.BuyManager.__init__(self)
        sell_manager.SellManager.__init__(self)
        order_manager.OrderManager.__init__(self)
        price_manager.PriceManager.__init__(self)
        trend_manager.TrendManager.__init__(self)
        logger.BotLogger.__init__(self)
        config_manager.ConfigManager.__init__(self)
        funds_manager.FundsManager.__init__(self)

        self.logger_message = ['']
        self.dry_run = DRY_RUN
        self.can_buy = CAN_BUY
        self.can_sell = CAN_SELL
        self.did_buy = False

    def _try_order(self, current_price):
        self._close_open_orders()
        average_buy_price = self.get_buy_price_average()
        self.update_trend(average_buy_price, current_price)
        self.update_funds()
        # BUY ORDER
        if self.can_buy:
            self.check_if_can_buy(average_buy_price, current_price)
        # SELL ORDER
        if self.can_sell:
            self.check_if_can_sell(average_buy_price, current_price)

    def run(self):
        has_data = False
        self.did_buy = False

        self.logger_message = ['']

        current_price = self.get_current_price()

        has_data = len(self.past_prices) > self.trend_size

        if has_data:
            self._try_order(current_price)

        self.log_info_message(self.logger_message)


def initialize_bot():
    bot = AlgoBot()
    bot.log_info('Running AlgoBot...')
    bot.get_config()
    bot.get_past_prices()
    bot.get_past_trends()
    bot.pending_orders_buy = bot.get_pending_orders('buy')
    bot.pending_orders_sell = bot.get_pending_orders('sell')
    bot.get_buy_orders()
    bot.get_completed_buy_orders()
    bot.get_sell_orders()
    bot.get_past_funds()
    return bot


def process_orders(bot):
    # orders = bot.process_pending_orders(bot.pending_orders_buy, 'buy')
    # bot.bought_orders += orders['complete']
    # bot.pending_orders_buy = orders['pending']
    # bot.save_buy_order()
    process_buy_orders(bot)
    process_sell_orders(bot)


def process_buy_orders(bot):
    bot.process_pending_buy_orders()


def process_sell_orders(bot):
    bot.process_pending_sell_orders()
    # clear_buy_orders = len(orders['complete']) > 0

    # bot.sell_orders += orders['complete']
    # bot.pending_orders_sell = orders['pending']
    # bot.save_sell_order(clear_buy_orders)


def main():
    bot = initialize_bot()
    count = PROCESS_TIMER
    while True:
        bot.get_config()

        if count % 30 == 0:
            process_orders(bot)

        if count >= PROCESS_TIMER:
            bot.bought_orders = bot.group_orders_by_price(bot.bought_orders)
            bot.save_buy_order()
            bot.run()
            count = 0

        time.sleep(1)
        count += 1


if __name__ == "__main__":
    main()
