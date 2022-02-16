import math

from pprint import pprint
from modules import luno, file_reader, mathematics


FACTOR = 10 ** 2


class BuyManager:
    def __init__(self) -> None:
        self.pending_orders_buy = []
        self.bought_orders = []
        self.completed_bought_orders = []

    def save_buy_order(self):
        file_reader.write_data({'orders': self.bought_orders}, 'buy_orders')

    def get_buy_orders(self):
        data = file_reader.read_data('buy_orders')
        self.bought_orders = data.get('orders') or []

    def save_completed_buy_orders(self):
        file_reader.write_data({'orders': self.completed_bought_orders}, 'completed_buy_orders')

    def get_completed_buy_orders(self):
        data = file_reader.read_data('completed_buy_orders')
        self.completed_bought_orders = data.get('orders') or []

    def get_buy_price_average(self):
        buy_prices = []
        for i in self.bought_orders:
            buy_price = float(i['limit_price'])
            fee_price = float(i['fee_base'])
            total_price = buy_price + fee_price
            buy_prices.append(total_price)
        return mathematics.get_mean(buy_prices) or 0.0

    def process_buy_order(self, current_price):

        self.logger_message.append(f'============================')
        self.logger_message.append(f'=== PROCESSING BUY ORDER ===')
        self.logger_message.append(f'============================')

        quantity = self.calculate_buy_quantity(current_price)
        self.logger_message.append(f'BUY QUANTITY: {quantity}')

        if quantity < self.min_trade_amount:
            self.logger_message.append(f'not enough funds for trade')
            return

        # fee = (float(luno.getPairFee(self.trading_pair)['taker_fee']) * float(quantity)) / 2
        fee = 0.01
        self.logger_message.append(f'FEE: {fee}')

        buy_price = float(current_price) - float(fee)
        buy_price = math.floor(buy_price * FACTOR) / FACTOR
        self.logger_message.append(f'BUY PRICE: {buy_price}')

        self.logger_message.append(f'TOTAL COST: {buy_price * quantity}')

        order = luno.create_buy_order(self.trading_pair, buy_price, quantity, dry_run=self.dry_run)
        if(not order.get('order_id')):
            self.logger_message.append(f'buy order couldn\'t be placed{order}')
            return

        order = luno.get_order(order['order_id'])
        if(not order.get('order_id')):
            self.logger_message.append(f'ORDER: {order}')
            return

        # if order.get('fee_base'):
        #     if float(order.get('fee_base')) > 0:
        #         print('Order contains fees, cancelling order')
        #         pprint(order)
        #         luno.close_open_order(order['order_id'])
        #         return

        funds = float(luno.getSpendableBalance())
        self.logger_message.append(f'FUNDS AFTER PURCHASE: {funds}')

        self.pending_orders_buy.append({'price': buy_price, 'quantity': quantity, 'funds': funds, **order})
        self.save_pending_order(self.pending_orders_buy, 'buy')

    def calculate_buy_quantity(self, current_price):
        purchase_percentage = self.purchase_percentage * (len(self.bought_orders) + 1)
        account_balance = float(luno.getSpendableBalance())
        funds_to_purchase = mathematics.get_percentage(account_balance, purchase_percentage)
        quantity = funds_to_purchase / current_price
        return round(quantity, 0)
