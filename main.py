from math import fabs
import time
from pprint import pprint
from modules import logger, luno, telegram
from classes import buy_manager, sell_manager, order_manager, price_manager
from classes import trend_manager, config_manager, funds_manager, profit_manager

TELEGRAM_TOKEN = '5265556776:AAEqBqxWcqfcp9vronKBCujHk2EWTULRpDA'
TELEGRAM_CHAT_ID = '469090152'


PROCESS_TIMER = 180
BUY_TIMER = 300
SELL_TIMER = 300
PROFIT_TIMER = 21600

# True
# False
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
    funds_manager.FundsManager,
    profit_manager.ProfitManager,
    telegram.Telegram):

    def __init__(self):
        buy_manager.BuyManager.__init__(self)
        sell_manager.SellManager.__init__(self)
        order_manager.OrderManager.__init__(self)
        price_manager.PriceManager.__init__(self)
        trend_manager.TrendManager.__init__(self)
        logger.BotLogger.__init__(self)
        config_manager.ConfigManager.__init__(self)
        funds_manager.FundsManager.__init__(self)
        profit_manager.ProfitManager.__init__(self)
        telegram.Telegram.__init__(self, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

        self.logger_message = ['']
        self.dry_run = DRY_RUN
        self.can_buy = CAN_BUY
        self.can_sell = CAN_SELL

    def _run_buy(self, weighted_price, current_price):
        if self.can_buy:
            self.check_if_can_buy(weighted_price, current_price)

    def _run_sell(self, weighted_price, current_price):
        if self.can_sell:
            self.check_if_can_sell(weighted_price, current_price)

    def has_data_for_transaction(self):
        return len(self.past_prices) > self.trend_size

    def run_update(self, current_price):
        self.get_total_profit_old()
        self.update_trend(current_price)
        self.update_funds()
        self._close_open_orders()
        self.log_info_message(self.logger_message)


def initialize_bot():
    bot = AlgoBot()
    bot.log_info('Running AlgoBot...')
    bot.get_config()
    bot.get_past_prices()
    bot.pending_orders_buy = bot.get_pending_orders('buy')
    bot.pending_orders_sell = bot.get_pending_orders('sell')
    bot.get_buy_orders()
    bot.get_past_orders()
    bot.get_past_profits()
    if not DRY_RUN:
        bot.send_message(f'CryptoBot started...\ndry run: {DRY_RUN}\ncan buy: {CAN_BUY}\ncan sell: {CAN_SELL}')
    return bot


def process_orders(bot):
    process_buy_orders(bot)
    process_sell_orders(bot)


def process_buy_orders(bot):
    bot.process_pending_buy_orders()


def process_sell_orders(bot):
    bot.process_pending_sell_orders()


def main():
    bot = initialize_bot()
    count = PROCESS_TIMER
    buy_counter = BUY_TIMER
    sell_counter = SELL_TIMER
    message_count = 0
    while True:
        print_log = False
        bot.get_config()

        weighted_price = 0.0
        current_price = 0.0

        if count % 10 == 0:
            process_orders(bot)

        if buy_counter >= BUY_TIMER or sell_counter >= SELL_TIMER:
            bot.logger_message = ['']
            weighted_price = bot.get_buy_price_average()
            current_price = bot.get_current_price()
            bot.run_update(current_price)
            print_log = True

        if buy_counter >= BUY_TIMER:
            bot.bought_orders = bot.group_orders_by_price(bot.bought_orders)
            bot.save_order(bot.bought_orders, 'buy')
            bot._run_buy(weighted_price, current_price)
            buy_counter = 0
            print_log = True

        if sell_counter >= SELL_TIMER:
            bot._run_sell(weighted_price, current_price)
            sell_counter = 0
            print_log = True

        if print_log:
            bot.log_info_message(bot.logger_message)

        if message_count >= PROFIT_TIMER:
            message = f'Daily Profit: {bot.get_profits_for_day()}\n'
            message += f'Total Profit: {bot.get_total_profits_summary()}'
            bot.send_message(message)
            message_count = 0

        time.sleep(1)
        count += 1
        buy_counter += 1
        sell_counter += 1
        message_count += 1


if __name__ == "__main__":
    telegramBot = telegram.Telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    try:
        main()
    except Exception as e:
        telegramBot.send_message(f'Error: {e}')
