import time
import schedule
import traceback
from pprint import pprint
from modules import logger, luno, bitstamp, telegram, mathematics
from classes import buy_manager, sell_manager, order_manager, price_manager
from classes import trend_manager, config_manager, funds_manager, profit_manager

TELEGRAM_TOKEN = '5265556776:AAEqBqxWcqfcp9vronKBCujHk2EWTULRpDA'
TELEGRAM_CHAT_ID = '469090152'


UPDATE_CONFIG_TIME = 30 # seconds
PROCESS_ORDERS_TIME = 10 # seconds
BUY_TIME = 2 # minutes
SELL_TIME = 2 # minutes
UPDATE_MESSAGE_TIME = 3 # hours
PROFIT_INCREASE_TIME = 1 # hours
# True
# False
DRY_RUN = False
CAN_BUY = True
CAN_SELL = True

botLogger = logger.BotLogger()


class AlgoBot(
    buy_manager.BuyManager,
    sell_manager.SellManager,
    order_manager.OrderManager,
    price_manager.PriceManager,
    trend_manager.TrendManager,
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
        config_manager.ConfigManager.__init__(self)
        funds_manager.FundsManager.__init__(self)
        profit_manager.ProfitManager.__init__(self)
        telegram.Telegram.__init__(self, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)

        self.logger = botLogger
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

    def run_update(self):
        self.get_total_profit_old()
        self.update_funds()
        self._close_open_orders()


def initialize_bot():
    bot = AlgoBot()
    bot.logger.log_info('Running AlgoBot...')
    bot.get_config()
    bot.get_prices()
    bot.pending_orders_buy = bot.get_pending_orders('buy')
    bot.pending_orders_sell = bot.get_pending_orders('sell')
    bot.get_buy_orders()
    bot.get_past_orders()
    bot.get_past_profits()
    if not DRY_RUN:
        bot.send_message(f'CryptoBot started...\ndry run: {DRY_RUN}\ncan buy: {CAN_BUY}\ncan sell: {CAN_SELL}')
    return bot


def process_orders(bot):
    bot.process_pending_buy_orders()
    bot.process_pending_sell_orders()


def handle_update(bot):
    bot.get_buy_price_average()
    bot.get_current_price()
    bot.run_update()


def handle_buy_orders(bot):
    handle_update(bot)
    bot.bought_orders = bot.group_orders_by_price(bot.bought_orders)
    bot.save_order(bot.bought_orders, 'buy')
    bot._run_buy(bot.weighted_price, bot.current_price)


def handle_sell_orders(bot):
    bot._run_sell(bot.weighted_price, bot.current_price)


def handle_update_message(bot):
    message = f'Daily Profit: {mathematics.round_down(bot.get_profits_for_day(), 2)}\n'
    message += f'Weekly Profit: {mathematics.round_down(bot.get_profits_for_week(), 2)}\n'
    message += f'Monthly Profit: {mathematics.round_down(bot.get_profits_for_month(), 2)}\n'
    message += f'Yearly Profit: {mathematics.round_down(bot.get_profits_for_year(), 2)}\n'
    message += f'Total Profit: {mathematics.round_down(bot.get_total_profits_summary(), 2)}'
    bot.send_message(message)


def handle_profit_increase(bot):
    bot.increase_profit_amount()


def main():
    bot = initialize_bot()
    bot.get_config()
    handle_update_message(bot)

    schedule.every(UPDATE_CONFIG_TIME).seconds.do(bot.get_config)
    schedule.every(PROCESS_ORDERS_TIME).seconds.do(process_orders, bot)
    schedule.every(BUY_TIME).minutes.do(handle_buy_orders, bot)
    schedule.every(SELL_TIME).minutes.do(handle_sell_orders, bot)
    schedule.every(UPDATE_MESSAGE_TIME).hours.do(handle_update_message, bot)
    # schedule.every(PROFIT_INCREASE_TIME).hours.do(handle_profit_increase, bot)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        botLogger.logger.log_warning(f'Error: {traceback.format_exc()}')
        telegram_bot = telegram.Telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
        telegram_bot.send_message(f'Error: {traceback.format_exc()}')
        time.sleep(120)
        main()
