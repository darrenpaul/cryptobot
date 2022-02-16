import os
import math

from pprint import pprint
from pathlib import Path
from modules import luno, file_reader, mathematics

FACTOR = 10 ** 2
DATA_DIRECTORY =  os.path.join(Path(__file__).parent.parent, 'data')


class SellManager:
    def __init__(self) -> None:
        self.sell_orders = []

    def save_sell_order(self):
        file_path = os.path.join(DATA_DIRECTORY, 'sell_orders.yml')
        data = {'orders': self.sell_orders}
        file_reader.write_yaml(data, file_path)

    def get_sell_orders(self):
        file_path = os.path.join(DATA_DIRECTORY, 'sell_orders.yml')
        if(not os.path.exists(file_path)):
            self.bought_orders = []
            return
        sell_orders = file_reader.read_yaml(file_path)
        self.sell_orders = sell_orders['orders']

    def process_sell_order(self, current_price, average_buy_price):
        print('== SELL ============================')
        print(f'Funds before: {float(luno.getSpendableBalance())}')

        total_quantity = math.floor(float(luno.getSpendableBalance('XRP')))
        if self.dry_run == True:
            total_quantity = 0.0
            for i in self.bought_orders:
                total_quantity = total_quantity + float(i['quantity'])
        print(f'Total Quantity: {total_quantity}')

        profit_value = mathematics.get_percentage(average_buy_price, self.profit_margin)
        print(f'Profit Value: {profit_value}')

        sell_price = float(average_buy_price) + float(profit_value)
        sell_price = math.floor(sell_price * FACTOR) / FACTOR
        print(f'Sell Price: {sell_price}')

        # SELL ORDER
        # if float(sell_price) > float(current_price):
        #     print('Sell Price is lower than current price')
        #     return

        # profit_sell_price = self.get_profit_sell_price(average_buy_price)
        # print(f'Sell Price: {profit_sell_price}')

        funds = float(luno.getSpendableBalance()) + float(float(sell_price) * float(total_quantity))
        print(f'Funds after: {funds}')

        order = luno.create_sell_order(self.trading_pair, sell_price, total_quantity, dry_run=self.dry_run)
        print(f'Order: {order}')

        if 'error' in order.keys():
            return

        self.bought_orders = []
        self.save_buy_order()

        sell_value = float(sell_price) * float(total_quantity)

        self.sell_orders.append(
            {
                'order_id': order['order_id'],
                'price': sell_price,
                'quantity': total_quantity,
                'funds': funds,
                'sell_value': sell_value,
                'average_buy_price': average_buy_price,
            }
        )
        self.save_sell_order()
