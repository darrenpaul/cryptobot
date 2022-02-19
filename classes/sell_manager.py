import math

from pprint import pprint
from modules import luno, file_reader, mathematics


FACTOR = 10 ** 2


class SellManager:
    def __init__(self) -> None:
        self.pending_orders_sell = []
        self.sell_orders = []
        self.sell_range_margin = 5

    def save_sell_order(self, clear_buy_orders):
        file_reader.write_data({'orders': self.sell_orders}, 'sell_orders')

        remove_ids = []
        incomplete_orders = []

        for order in self.pending_orders_sell:
            if order.get('order_ids'):
                remove_ids.append(order.get('order_ids'))

        for order in self.bought_orders:
            if order['order_id'] not in remove_ids:
                incomplete_orders.append(order)

        if clear_buy_orders:
            self.completed_bought_orders = self.completed_bought_orders + self.bought_orders
            self.save_completed_buy_orders()

            self.bought_orders = incomplete_orders
            self.save_buy_order()

    def get_sell_orders(self):
        data = file_reader.read_data('sell_orders')
        self.sell_orders = data.get('orders') or []

    def process_pending_sell_orders(self):
        incomplete_orders = []
        complete_orders = []
        order_ids = []

        for order in self.pending_orders_sell:
            query_order = luno.get_order(order['order_id'])
            order = {**order, **query_order}
            if order.get('status') == 'COMPLETE':
                complete_orders.append({**order})
                order_ids += order.get('order_ids')
            else:
                incomplete_orders.append({**order})

        self.complete_buy_orders(order_ids)


        # for i in pending_orders:
        #     order = luno.get_order(i['order_id'])
        #     order = i # DELETE
        #     counter = float(order.get('counter'))
        #     if order.get('status') == 'COMPLETE' and counter > 0:
        #         complete_orders.append({**i, **order})
        #     else:
        #         if counter > 0.0:
        #             incomplete_orders.append({**i, **order})

        # pending_orders = incomplete_orders
        # self.save_pending_order(pending_orders, order_type)
        # return {'pending': pending_orders, 'complete': complete_orders}

    def process_sell_order(self, average_buy_price):
        self.logger_message.append(f'=============================')
        self.logger_message.append(f'=== PROCESSING SELL ORDER ===')
        self.logger_message.append(f'=============================')

        total_quantity = math.floor(float(luno.getSpendableBalance('XRP')))
        if self.dry_run == True:
            total_quantity = 0.0
            for i in self.bought_orders:
                total_quantity = total_quantity + float(i['quantity'])
        self.logger_message.append(f'SELL QUANTITY: {total_quantity}')

        profit_value = mathematics.get_percentage(average_buy_price, self.profit_margin)
        self.logger_message.append(f'PROFIT VALUE: {profit_value}')

        sell_price = float(average_buy_price) + float(profit_value)
        sell_price = math.floor(sell_price * FACTOR) / FACTOR
        self.logger_message.append(f'SELL PRICE: {sell_price}')

        # SELL ORDER
        # if float(sell_price) > float(current_price):
        #     print('Sell Price is lower than current price')
        #     return

        # profit_sell_price = self.get_profit_sell_price(average_buy_price)
        # print(f'Sell Price: {profit_sell_price}')

        order = luno.create_sell_order(self.trading_pair, sell_price, total_quantity, dry_run=self.dry_run)
        self.logger_message.append(f'ORDER: {order}')

        if 'error' in order.keys():
            return

        sell_value = float(sell_price) * float(total_quantity)

        self.pending_orders_sell.append(
            {
                'order_id': order['order_id'],
                'price': sell_price,
                'quantity': total_quantity,
                'sell_value': sell_value,
                'average_buy_price': average_buy_price,
            }
        )
        self.save_pending_order(self.pending_orders_sell, 'sell')

    def process_possible_sell_orders(self, current_price):
        self.logger_message.append(f'=============================')
        self.logger_message.append(f'=== PROCESSING POSSIBLE SELL ORDER ===')
        self.logger_message.append(f'=============================')
        possible_orders = []
        total_quantity = 0.0
        order_ids = []

        start = float(current_price) - float(self.sell_range_margin)
        end = float(current_price) + float(self.sell_range_margin)

        for order in self.bought_orders:
            order_price = float(order['limit_price'])
            order_quantity = float(order['quantity'])
            order_id = order['order_id']
            if order_price > start and order_price < end:
                possible_orders.append(order)
                total_quantity += order_quantity
                order_ids.append(order_id)

        if len(possible_orders) > 0:
            sell_price = mathematics.get_weighted_average(possible_orders, 'limit_price', 'quantity')
            if(current_price < sell_price):
                return
            sell_price = current_price + 0.01
            order = luno.create_sell_order(self.trading_pair, sell_price, total_quantity, dry_run=self.dry_run)

            self.logger_message.append(f'ORDER: {order}')

            sell_value = float(sell_price) * float(total_quantity)

            self.pending_orders_sell.append(
                {
                    'order_id': order['order_id'],
                    'price': sell_price,
                    'quantity': total_quantity,
                    'sell_value': sell_value,
                    'order_ids': order_ids
                }
            )
            self.save_pending_order(self.pending_orders_sell, 'sell')

    def check_if_can_sell(self, average_buy_price, current_price):
        if self.did_buy:
            return
        if len(self.bought_orders) == 0:
            return

        if float(average_buy_price) < float(current_price):
            pass
            # self.process_sell_order(average_buy_price)
        else:
            self.process_possible_sell_orders(current_price)