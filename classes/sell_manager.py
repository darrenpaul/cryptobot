from pprint import pprint
from modules import luno, file_reader, mathematics, order_utils


class SellManager:
    def __init__(self) -> None:
        self.pending_orders_sell = []
        self.sell_orders = []
        self.sell_range_margin = 5

    def _get_quantity(self):
        quantity = mathematics.round_down(luno.getSpendableBalance('XRP'), 2)
        if self.dry_run == True:
            quantity = 0.0
            for i in self.bought_orders:
                quantity = quantity + float(i['quantity'])
        self.logger_message.append(f'SELL QUANTITY: {quantity}')
        return quantity

    def _get_sell_price(self, weighted_price):
        profit_value = mathematics.get_percentage(weighted_price, self.profit_margin) + 0.01
        self.logger_message.append(f'PROFIT VALUE: {profit_value}')

        sell_price = float(weighted_price) + float(profit_value)
        sell_price = mathematics.round_down(sell_price, 2)
        self.logger_message.append(f'SELL PRICE: {sell_price}')
        return sell_price

    def _get_possible_sell_orders(self, price):
        orders = []
        end = float(price) + float(self.sell_range_margin)

        for order in self.bought_orders:
            order_price = float(order['limit_price'])
            if order_price < end:
                orders.append(order)
        return orders

    def _create_sell_order(self, price, quantity):
        simple_order = luno.create_sell_order(self.trading_pair, price, quantity, dry_run=self.dry_run)
        if simple_order.get('order_id'):
            order = luno.get_order(simple_order['order_id'])
            self.logger_message.append(f'ORDER: {order}')
            return order

    def save_sell_order(self):
        file_reader.write_data({'orders': self.sell_orders}, 'sell_orders')

    def get_sell_orders(self):
        data = file_reader.read_data('sell_orders')
        self.sell_orders = data.get('orders') or []

    def process_pending_sell_orders(self):
        pending_orders = order_utils.add_key_to_dict(self.pending_orders_sell, 'cancel_count', 1)
        pending_orders = order_utils.run_function_on_list_items(pending_orders, 'order_id', luno.get_order)

        incomplete_orders = order_utils.get_list_of_dict_when_condition_false(pending_orders, 'status', 'COMPLETE')

        complete_orders = order_utils.get_list_of_dict_when_condition_true(pending_orders, 'status', 'COMPLETE')
        complete_orders = order_utils.get_list_of_dict_when_condition_greater(complete_orders, 'counter', 1.0)

        order_ids = []
        for order in pending_orders:
            ids = order.get('order_ids')
            if ids:
                order_ids.extend(ids)

        self.pending_orders_sell = incomplete_orders
        self.save_pending_order(self.pending_orders_sell, 'sell')

        self.sell_orders = complete_orders
        self.save_sell_order()

        self.past_orders = [*self.past_orders, *complete_orders]
        self.save_past_orders()

        if len(complete_orders) > 0:
            self.save_current_funds(complete_orders)
            self.complete_buy_orders(order_ids)

    def process_sell_order(self, weighted_price):
        self.logger_message.append(f'=============================')
        self.logger_message.append(f'=== PROCESSING SELL ORDER ===')
        self.logger_message.append(f'=============================')

        quantity = self._get_quantity()
        price = self._get_sell_price(weighted_price)

        order = self._create_sell_order(price, quantity)

        self.pending_orders_sell.append(
            {
                'price': price,
                'quantity': quantity,
                'weighted_price': weighted_price,
                **order
            }
        )
        self.save_pending_order(self.pending_orders_sell, 'sell')

    def process_possible_sell_orders(self, price, quantity, orders, ids):
        self.logger_message.append(f'=============================')
        self.logger_message.append(f'=== PROCESSING PSO ==========')
        self.logger_message.append(f'=============================')

        order = self._create_sell_order(price, quantity)

        self.pending_orders_sell.append(
            {
                'price': price,
                'quantity': quantity,
                'order_ids': ids,
                'orders': orders,
                **order
            }
        )
        self.save_pending_order(self.pending_orders_sell, 'sell')

    def check_if_can_sell(self, weighted_price, current_price):
        if self.did_buy:
            return
        if len(self.bought_orders) == 0:
            return
        if len(self.pending_orders_sell) > 0:
            return
        if float(weighted_price) < float(current_price):
            self.process_sell_order(weighted_price)
        else:
            self.check_for_possible_sell_orders(current_price)

    def check_for_possible_sell_orders(self, current_price):
        orders = self._get_possible_sell_orders(current_price)
        total_quantity = order_utils.get_dict_value_total(orders, 'quantity')
        order_ids = order_utils.get_list_of_dict_values(orders, 'order_id')

        if len(orders) > 0:
            weighted_price = mathematics.get_weighted_average(orders, 'limit_price', 'quantity')
            sell_price = self._get_sell_price(weighted_price)

            if sell_price > current_price:
                return

            self.process_possible_sell_orders(sell_price, total_quantity, orders, order_ids)
