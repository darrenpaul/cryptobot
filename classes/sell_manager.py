from pprint import pprint
from modules import luno, file_reader, mathematics, order_utils


class SellManager:
    def __init__(self) -> None:
        self.pending_orders_sell = []
        self.sell_orders = []
        self.sell_group_margin = 5

    def _get_quantity(self):
        quantity = mathematics.round_down(luno.getSpendableBalance('XRP'), 2)
        if self.dry_run == True:
            quantity = 0.0
            for i in self.bought_orders:
                quantity = quantity + float(i['quantity'])
        self.logger_message.append(f'SELL QUANTITY: {quantity}')
        return float(int(quantity))

    def _get_sell_price(self, weighted_price):
        profit_value = self.profit_amount
        # profit_value = mathematics.get_percentage(weighted_price, self.profit_percentage) + 0.02

        sell_price = float(weighted_price) + float(profit_value)
        sell_price = mathematics.round_up(sell_price)
        self.logger_message.append(f'SELL PRICE: {sell_price}')
        return sell_price

    def _get_possible_sell_orders(self, price):
        orders = []
        end = float(price)

        for order in self.bought_orders:
            order_price = float(order['limit_price'])
            if order_price <= end:
                orders.append(order)
        return orders

    def _create_sell_order(self, price, quantity):
        simple_order = luno.create_sell_order(self.trading_pair, price, quantity, dry_run=self.dry_run)
        print(simple_order)
        if simple_order.get('order_id'):
            order = luno.get_order(simple_order['order_id'])
            self.logger_message.append(f'ORDER: {order}')
            return order

    def process_pending_sell_orders(self):
        updated_pending_orders = order_utils.update_order_details(self.pending_orders_sell)
        pending_orders = order_utils.update_cancel_count(updated_pending_orders)

        incomplete_orders = order_utils.get_incomplete_orders(pending_orders)

        complete_orders = order_utils.get_complete_orders(pending_orders, 'SELL')

        order_ids = order_utils.get_order_ids(pending_orders)

        if len(complete_orders) > 0:
            profit = self.get_profit(complete_orders)
            self.add_profit(profit)

        self.pending_orders_sell = incomplete_orders
        self.save_pending_order(self.pending_orders_sell, 'sell')

        self.past_orders = [*self.past_orders, *complete_orders]
        self.save_past_orders()

        if len(complete_orders) > 0:
            self.complete_buy_orders(order_ids)

    def process_sell_order(self, current_price, weighted_price):
        self.logger_message.append(f'=============================')
        self.logger_message.append(f'=== PROCESSING SELL ORDER ===')
        self.logger_message.append(f'=============================')

        quantity = self._get_quantity()

        sell_price = weighted_price
        if current_price > weighted_price:
            sell_price = current_price

        price = self._get_sell_price(sell_price)

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
        if order and order.get('order_id'):
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
        if len(self.bought_orders) == 0:
            return
        if len(self.pending_orders_sell) > 0:
            return
        # if float(weighted_price) < float(current_price):
        #     self.process_sell_order(current_price, weighted_price)
        # else:
        self.check_for_possible_sell_orders(current_price)

    def check_for_possible_sell_orders(self, current_price):
        orders = self._get_possible_sell_orders(current_price)
        total_quantity = order_utils.get_dict_value_total(orders, 'quantity')
        order_ids = order_utils.get_list_of_dict_values(orders, 'order_id')

        if len(orders) > 0:
            weighted_price = mathematics.get_weighted_average(orders, 'limit_price', 'quantity')
            sell_price = self._get_sell_price(weighted_price)
            if sell_price < current_price:
                sell_price = current_price + self.profit_amount

            self.process_possible_sell_orders(sell_price, total_quantity, orders, order_ids)
