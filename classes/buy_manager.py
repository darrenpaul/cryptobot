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

    def save_completed_buy_orders(self):
        file_reader.write_data({'orders': self.completed_bought_orders}, 'completed_buy_orders')

    def get_buy_orders(self):
        data = file_reader.read_data('buy_orders')
        self.bought_orders = data.get('orders') or []

    def get_completed_buy_orders(self):
        data = file_reader.read_data('completed_buy_orders')
        self.completed_bought_orders = data.get('orders') or []

    def get_buy_price_average(self):
        fee = 0.01
        if len(self.bought_orders) == 0:
            return 0
        weighted_price = mathematics.get_weighted_average(self.bought_orders, 'limit_price', 'quantity') + fee
        rounded_price = math.floor(weighted_price * FACTOR) / FACTOR
        self.logger_message.append(f'AVERAGE BUY PRICE: {rounded_price}')
        return rounded_price

    def get_highest_buy_price(self):
        prices = []

        for order in self.bought_orders:
            prices.append(float(order['limit_price']))
        return mathematics.get_max(prices)

    def price_in_buy_margin(self, current_price):
        can_buy = True
        _buy_margin = self.buy_margin * len(self.bought_orders)
        for order in self.bought_orders:
            price = float(order['limit_price'])
            start = price - _buy_margin
            end = price + _buy_margin
            if current_price > start and price < end:
                can_buy = False
        return can_buy

    def process_buy_order(self, current_price, quantity):
        self.logger_message.append(f'============================')
        self.logger_message.append(f'=== PROCESSING BUY ORDER ===')
        self.logger_message.append(f'============================')

        # fee = (float(luno.getPairFee(self.trading_pair)['taker_fee']) * float(quantity)) / 2
        # self.logger_message.append(f'FEE: {fee}')
        fee = 0.01

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

        self.logger_message.append(f'FUNDS AFTER PURCHASE: {self.funds}')

        self.pending_orders_buy.append({'price': buy_price, 'quantity': quantity, 'funds': self.funds, **order})
        self.save_pending_order(self.pending_orders_buy, 'buy')

    def process_pending_buy_orders(self):
        incomplete_orders = []
        complete_orders = []
        for i in self.pending_orders_buy:
            order = luno.get_order(i['order_id'])
            counter = float(order.get('counter'))

            if order.get('status') == 'COMPLETE':
                if counter > 0.0:
                    complete_orders.append({**i, **order})
            else:
                incomplete_orders.append({**i, **order})

        self.bought_orders = complete_orders + self.bought_orders
        self.pending_orders_buy = incomplete_orders
        self.save_buy_order()
        self.save_pending_order(self.pending_orders_buy, 'buy')

    def calculate_buy_quantity(self, current_price):
        purchase_percentage = self.purchase_percentage * (len(self.bought_orders) + 1)
        account_balance = self.funds
        funds_to_purchase = mathematics.get_percentage(account_balance, purchase_percentage)
        quantity = funds_to_purchase / current_price
        return round(quantity, 0)

    def check_if_can_buy(self, average_buy_price, current_price):
        highest_buy_price = self.get_highest_buy_price()
        if highest_buy_price and current_price > highest_buy_price:
            return False

        quantity = self.calculate_buy_quantity(current_price)
        self.logger_message.append(f'BUY QUANTITY: {quantity}')
        if quantity < float(self.min_trade_amount):
            self.logger_message.append(f'not enough funds for trade')
            return False

        price_in_margin = self.price_in_buy_margin(current_price)
        if price_in_margin == False:
            return False

        if self.trend <= self.trend_margin and self.trend >= self.min_trend_margin or \
            self.purchase_trend <= self.purchase_trend_margin:
            if float(average_buy_price) != float(current_price):
                self.process_buy_order(current_price, quantity)
                self.did_buy = True

    def complete_buy_orders(self, order_ids):
        buy_orders = []
        if len(order_ids) > 0:
            for order in self.bought_orders:
                order_id = order.get('order_id')
                if order_id in order_ids:
                    continue
                buy_orders.append(order)
        self.bought_orders = buy_orders
        self.save_buy_order()