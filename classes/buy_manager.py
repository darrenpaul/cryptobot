from pprint import pprint
from modules import luno, mathematics, order_utils


class BuyManager:
    def __init__(self) -> None:
        self.pending_orders_buy = []
        self.bought_orders = []
        self.weighted_price = 0.0

    def _get_buy_price(self, current_price):
        fee = float(current_price) / float(self.buy_price_margin)
        buy_price = float(current_price) - mathematics.round_down(fee, 2)
        buy_price = mathematics.round_down(buy_price, 2)
        self.log_info(f'BUY PRICE: {buy_price}')
        return buy_price

    def get_buy_orders(self):
        data = self.get_orders('buy')
        self.bought_orders = data.get('orders') or []

    def get_buy_price_average(self):
        if len(self.bought_orders) == 0:
            return 0
        weighted_price = mathematics.get_weighted_average(self.bought_orders, 'limit_price', 'quantity')
        rounded_price = mathematics.round_down(weighted_price, 2)
        self.log_info(f'AVERAGE BUY PRICE: {rounded_price}')
        self.weighted_price = rounded_price

    def get_highest_buy_price(self):
        prices = []

        for order in self.bought_orders:
            prices.append(float(order['limit_price']))
        return mathematics.get_max(prices)

    def price_in_buy_margin(self, current_price):
        can_buy = True
        _buy_margin = self.buy_margin * len(self.bought_orders)
        margins = []
        for order in self.bought_orders:
            price = float(order['limit_price'])
            start = mathematics.round_up(price - _buy_margin)
            end = mathematics.round_up(price + _buy_margin)
            margins.append(start)
            margins.append(end)
            if current_price > start and price < end:
                can_buy = False

        min_margin = mathematics.get_min(margins)
        max_margin = mathematics.get_max(margins)
        self.log_info(f'CAN\'T BUY BETWEEN: {min_margin} - {max_margin}')
        return can_buy

    def process_buy_order(self, current_price, quantity):
        self.log_info(f'============================')
        self.log_info(f'=== PROCESSING BUY ORDER ===')
        self.log_info(f'============================')

        buy_price = self._get_buy_price(current_price)

        self.log_info(f'TOTAL COST: {buy_price * quantity}')

        order = luno.create_buy_order(self.trading_pair, buy_price, quantity, dry_run=self.dry_run)

        if(not order.get('order_id')):
            self.log_info(f'buy order couldn\'t be placed{order}')
            self.log_info(f'ORDER: {order}')
            return

        order = luno.get_order(order['order_id'])

        self.log_info(f'FUNDS AFTER PURCHASE: {self.funds}')

        self.pending_orders_buy.append({'price': buy_price, 'quantity': quantity, 'funds': self.funds, **order})
        self.save_pending_order(self.pending_orders_buy, 'buy')

    def process_pending_buy_orders(self):
        incomplete_orders = []
        complete_orders = []

        updated_pending_orders = order_utils.update_order_details(self.pending_orders_buy)
        pending_orders = order_utils.update_cancel_count(updated_pending_orders)

        incomplete_orders = order_utils.get_incomplete_orders(pending_orders)

        complete_orders = order_utils.get_complete_orders(pending_orders, 'BUY')

        self.pending_orders_buy = incomplete_orders
        self.save_pending_order(self.pending_orders_buy, 'buy')

        self.bought_orders =  self.bought_orders + complete_orders
        self.save_order(self.bought_orders, 'buy')

        self.past_orders = [*self.past_orders, *complete_orders]
        self.save_past_orders()

    def calculate_buy_quantity(self, current_price):
        purchase_percentage = self.purchase_percentage * (len(self.bought_orders) + 1)
        if purchase_percentage > 100.00:
            purchase_percentage = 100.00

        account_balance = self.funds
        funds_to_purchase = mathematics.get_percentage(account_balance, purchase_percentage)
        quantity = mathematics.round_down(funds_to_purchase / current_price, 0)
        self.log_info(f'BUY QUANTITY: {quantity}')
        return mathematics.round_up(quantity, 0)

    def check_if_can_buy(self, weighted_price, current_price):
        if len(self.pending_orders_buy) > 0:
            return False

        highest_buy_price = self.get_highest_buy_price()
        if highest_buy_price and current_price > highest_buy_price:
            return False

        quantity = self.calculate_buy_quantity(current_price)
        if quantity < float(self.min_trade_amount):
            self.log_info(f'not enough funds for trade')
            return False

        price_in_margin = self.price_in_buy_margin(current_price)
        if price_in_margin == False:
            return False

        if weighted_price > 0.0:
            if float(weighted_price) < float(current_price):
                return False

        if self.check_if_trend_in_range():
            self.process_buy_order(current_price, quantity)

    def complete_buy_orders(self, order_ids):
        buy_orders = []
        if len(order_ids) > 0:
            for order in self.bought_orders:
                order_id = order.get('order_id')
                if order_id in order_ids:
                    continue
                buy_orders.append(order)
        self.bought_orders = buy_orders
        self.save_order(self.bought_orders, 'buy')