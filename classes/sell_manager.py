import math

from pprint import pprint
from modules import luno, file_reader, mathematics


FACTOR = 10 ** 2


class SellManager:
    def __init__(self) -> None:
        self.pending_orders_sell = []
        self.sell_orders = []

    def save_sell_order(self, clear_buy_orders):
        file_reader.write_data({'orders': self.sell_orders}, 'sell_orders')
        if clear_buy_orders:
            self.completed_bought_orders = self.completed_bought_orders + self.bought_orders
            self.save_completed_buy_orders()

            self.bought_orders = []
            self.save_buy_order()

    def get_sell_orders(self):
        data = file_reader.read_data('sell_orders')
        self.sell_orders = data.get('orders') or []

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

        funds = float(luno.getSpendableBalance()) + float(float(sell_price) * float(total_quantity))
        print(f'Funds after: {funds}')

        self.pending_orders_sell.append(
            {
                'order_id': order['order_id'],
                'price': sell_price,
                'quantity': total_quantity,
                'funds': funds,
                'sell_value': sell_value,
                'average_buy_price': average_buy_price,
            }
        )
        self.save_pending_order(self.pending_orders_sell, 'sell')
