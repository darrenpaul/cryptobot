from modules import luno, file_reader, mathematics


class SellManager:
    def __init__(self) -> None:
        self.pending_orders_sell = []
        self.sell_orders = []
        self.sell_range_margin = 5

    def save_sell_order(self):
        file_reader.write_data({'orders': self.sell_orders}, 'sell_orders')

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
            counter = float(order.get('counter'))

            cancel_count = order.get('cancel_count') or 0
            cancel_count += 1

            if order.get('status') == 'COMPLETE':
                if counter > 0.0:
                    complete_orders.append({**order, 'cancel_count': cancel_count})
                    ids = order.get('order_ids')
                    if ids:
                        order_ids = order_ids + ids
            else:
                incomplete_orders.append({**order, 'cancel_count': cancel_count})

        self.pending_orders_sell = incomplete_orders
        self.sell_orders = complete_orders
        self.save_pending_order(self.pending_orders_sell, 'sell')
        self.save_sell_order()
        if len(complete_orders) > 0:
            self.save_current_funds(complete_orders)
            self.complete_buy_orders(order_ids)

    def process_sell_order(self, average_buy_price):
        self.logger_message.append(f'=============================')
        self.logger_message.append(f'=== PROCESSING SELL ORDER ===')
        self.logger_message.append(f'=============================')

        total_quantity = mathematics.round_down(luno.getSpendableBalance('XRP'), 2)
        if self.dry_run == True:
            total_quantity = 0.0
            for i in self.bought_orders:
                total_quantity = total_quantity + float(i['quantity'])
        self.logger_message.append(f'SELL QUANTITY: {total_quantity}')

        profit_value = mathematics.get_percentage(average_buy_price, self.profit_margin)
        self.logger_message.append(f'PROFIT VALUE: {profit_value}')

        sell_price = float(average_buy_price) + float(profit_value)
        sell_price = mathematics.round_down(sell_price, 2)
        self.logger_message.append(f'SELL PRICE: {sell_price}')

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

    def process_possible_sell_orders(self, price, quantity, orders, ids):
        self.logger_message.append(f'=============================')
        self.logger_message.append(f'=== PROCESSING POSSIBLE SELL ORDER ===')
        self.logger_message.append(f'=============================')
        order = luno.create_sell_order(self.trading_pair, price, quantity, dry_run=self.dry_run)

        self.logger_message.append(f'ORDER: {order}')

        sell_value = float(price) * float(quantity)

        self.pending_orders_sell.append(
            {
                'order_id': order['order_id'],
                'price': price,
                'quantity': quantity,
                'sell_value': sell_value,
                'order_ids': ids
            }
        )
        self.save_pending_order(self.pending_orders_sell, 'sell')

    def check_if_can_sell(self, average_buy_price, current_price):
        if self.did_buy:
            return
        if len(self.bought_orders) == 0:
            return

        if float(average_buy_price) < float(current_price):
            self.process_sell_order(average_buy_price)
        else:
            self.check_for_possible_sell_orders(current_price)

    def check_for_possible_sell_orders(self, current_price):
        orders = []
        total_quantity = 0.0
        order_ids = []

        end = float(current_price) + float(self.sell_range_margin)

        for order in self.bought_orders:
            order_price = float(order['limit_price'])
            order_quantity = float(order['quantity'])
            order_id = order['order_id']

            if order_price < end:
                orders.append(order)
                total_quantity += order_quantity
                order_ids.append(order_id)

        if len(orders) > 0:
            weighted_price = mathematics.get_weighted_average(orders, 'limit_price', 'quantity')
            profit_value = mathematics.get_percentage(weighted_price, self.pso_profit)

            sell_price = float(profit_value) + float(weighted_price)
            sell_price = mathematics.round_down(sell_price, 2)

            self.logger_message.append(f'CAN SELL AT: {sell_price}')
            if sell_price > current_price:
                return

            self.process_possible_sell_orders(sell_price, total_quantity, orders, order_ids)
