import uuid
from modules import luno, file_reader


class OrderManager:
    def __init__(self):
        self.trading_pair = 'XBTZAR'
        self.profit_margin = 2
        self.purchase_percentage = 5
        self.past_orders = []

    def save_order(self, orders, order_type):
        file_reader.write_data({'orders': orders}, f'{order_type}_orders')

    def get_orders(self, order_type):
        return file_reader.read_data(f'{order_type}_orders')

    def save_past_orders(self):
        self.save_order(self.past_orders, 'past')

    def get_past_orders(self):
        self.past_orders = self.get_orders('past').get('orders') or []

    def save_pending_order(self, data, order_type):
        file_reader.write_data({'orders': data}, f'pending_orders_{order_type}')

    def get_pending_orders(self, order_type):
        data = file_reader.read_data(f'pending_orders_{order_type}')
        return data.get('orders') or []

    def process_pending_orders(self, pending_orders, order_type):
        incomplete_orders = []
        complete_orders = []
        for i in pending_orders:
            order = luno.get_order(i['order_id'])
            counter = float(order.get('counter'))
            if order.get('status') == 'COMPLETE' and counter > 0:
                complete_orders.append({**i, **order})
            else:
                if counter > 0.0:
                    incomplete_orders.append({**i, **order})

        pending_orders = incomplete_orders
        self.save_pending_order(pending_orders, order_type)
        return {'pending': pending_orders, 'complete': complete_orders}

    def group_orders_by_price(self, orders_to_sort):
        sorted_orders = {}
        for order in orders_to_sort:
            price = order['limit_price']
            if price not in sorted_orders:
                sorted_orders[price] = []
            sorted_orders[price].append(order)

        grouped_orders = []
        for key, val in sorted_orders.items():
            order_id = uuid.uuid4()
            price = key
            quantity = 0.0
            funds = 0.0
            for order in val:
                order_id = order['order_id']
                quantity += float(order['quantity'])
                order_funds = order.get('funds')
                if order_funds:
                    funds += float(order_funds)

            grouped_orders.append(
                {
                    'order_id': order_id,
                    'limit_price': price,
                    'quantity': quantity, 
                    'price': price,
                    'counter': 1.0,
                    'funds': funds
                }
            )

        return grouped_orders

    def _close_open_orders(self):
        buy_orders = []
        sell_orders = []

        for order in [*self.pending_orders_buy, *self.pending_orders_sell]:
            cancel_count = order.get('cancel_count') or 0
            order_id = order.get('order_id')
            if cancel_count == self.cancel_count:
                luno.close_open_order(order['order_id'])
                self.logger_message.append(f'CLOSING ORDER: {order_id}')
            cancel_count += 1
            if order.get('side') == 'SELL':
                buy_orders.append({**order, **{'cancel_count': cancel_count}})
            if order.get('side') == 'BUY':
                sell_orders.append({**order, **{'cancel_count': cancel_count}})

        self.pending_orders_buy = buy_orders
        self.save_pending_order(self.pending_orders_buy, 'buy')
        self.pending_orders_sell = sell_orders
        self.save_pending_order(self.pending_orders_sell, 'sell')
        

        # cancelled_orders = luno.close_open_orders(self.trading_pair)
        # if len(cancelled_orders) > 0:
        #     # self.pending_orders_buy = []
        #     # self.pending_orders_sell = []
        #     # self.save_pending_order(self.pending_orders_buy, 'buy')
        #     # self.save_pending_order(self.pending_orders_sell, 'sell')
        #     self.logger_message.append(f'cancelled open orders {cancelled_orders}')