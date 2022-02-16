import os
import math

from pprint import pprint
from pathlib import Path
from modules import luno, file_reader, mathematics

FACTOR = 10 ** 2
DATA_DIRECTORY =  os.path.join(Path(__file__).parent.parent, 'data')

class BuyManager:
    def __init__(self) -> None:
        self.pending_orders = []
        self.bought_orders = []

    def save_pending_order(self):
        file_path = os.path.join(DATA_DIRECTORY, 'pending_orders.yml')
        data = {'orders': self.pending_orders}
        file_reader.write_yaml(data, file_path)

    def get_pendings_orders(self):
        file_path = os.path.join(DATA_DIRECTORY, 'pending_orders.yml')
        if(not os.path.exists(file_path)):
            self.pending_orders = []
            return
        pending_orders = file_reader.read_yaml(file_path)
        self.pending_orders = pending_orders['orders']

    def save_buy_order(self):
        file_path = os.path.join(DATA_DIRECTORY, 'buy_orders.yml')
        data = {'orders': self.bought_orders}
        file_reader.write_yaml(data, file_path)

    def get_buy_orders(self):
        file_path = os.path.join(DATA_DIRECTORY, 'buy_orders.yml')
        if(not os.path.exists(file_path)):
            self.bought_orders = []
            return
        bought_orders = file_reader.read_yaml(file_path)
        self.bought_orders = bought_orders['orders']

    def get_buy_price_average(self):
        buy_prices = []
        for i in self.bought_orders:
            buy_price = float(i['limit_price'])
            fee_price = float(i['fee_base'])
            total_price = buy_price + fee_price
            buy_prices.append(total_price)
        return mathematics.get_mean(buy_prices)

    def process_buy_order(self, current_price):
        print('== BUY ============================')

        print(f'Funds Before: {float(luno.getSpendableBalance())}')

        quantity = self.calculate_buy_quantity(current_price)
        print(f'Buy Quantity: {quantity}')

        if quantity < self.min_trade_amount:
            print('Not enough funds for trade')
            return

        fee = (float(luno.getPairFee(self.trading_pair)['taker_fee']) * float(quantity)) / 2
        print(f'Fee: {fee}')

        buy_price = float(current_price) - float(fee)
        buy_price = math.floor(buy_price * FACTOR) / FACTOR
        print(f'Buy Price: {buy_price}')

        print(f'Total cost: {buy_price * quantity}')

        order = luno.create_buy_order(self.trading_pair, buy_price, quantity, dry_run=self.dry_run)
        if(not order.get('order_id')):
            print('Buy order couldn\'t be placed')
            pprint(order)
            return

        order = luno.get_order(order['order_id'])
        if(not order.get('order_id')):
            print(order)
            return

        # if order.get('fee_base'):
        #     if float(order.get('fee_base')) > 0:
        #         print('Order contains fees, cancelling order')
        #         pprint(order)
        #         luno.close_open_order(order['order_id'])
        #         return

        funds = float(luno.getSpendableBalance())
        print(f'Funds after: {float(luno.getSpendableBalance())}')

        self.pending_orders.append({'price': buy_price, 'quantity': quantity, 'funds': funds, **order})
        self.save_pending_order()

    def process_pending_orders(self):
        incomplete_orders = []
        for i in self.pending_orders:
            order = luno.get_order(i['order_id'])
            if order.get('state') == 'COMPLETE':
                self.bought_orders.append({**order, **i})
            else:
                incomplete_orders.append(i)
        
        self.pending_orders = incomplete_orders
        self.save_pending_order()

        self.save_buy_order()

    def calculate_buy_quantity(self, current_price):
        purchase_percentage = self.purchase_percentage * (len(self.bought_orders) + 1)
        account_balance = float(luno.getSpendableBalance())
        funds_to_purchase = mathematics.get_percentage(account_balance, purchase_percentage)
        quantity = funds_to_purchase / current_price
        return round(quantity, 0)
