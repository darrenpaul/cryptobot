import uuid
from modules import luno, file_reader


class OrderManager:
    def __init__(self):
        self.trading_pair = 'XBTZAR'
        self.profit_margin = 2
        self.purchase_percentage = 5
        self.funds = float(luno.getSpendableBalance())

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
            order = i # DELETE
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
            for order in val:
                order_id = order['order_id']
                quantity += float(order['quantity'])

            grouped_orders.append({'order_id': order_id, 'limit_price': price, 'quantity': quantity, 'price': price})

        return grouped_orders
