import os

from pathlib import Path
from datetime import datetime
from modules import luno, file_reader, mathematics


DATA_DIRECTORY =  os.path.join(Path(__file__).parent.parent, 'data')


class PriceManager:
    def __init__(self) -> None:
        self.past_prices = []
        self.prices = []
        self.current_price = 0.0

    def _save_prices(self):
        file_path = os.path.join(DATA_DIRECTORY, 'prices.yml')
        data = {'prices': self.prices}
        file_reader.write_yaml(data, file_path)

    # def get_past_prices(self):
    #     file_path = os.path.join(DATA_DIRECTORY, 'past_prices.yml')
    #     if(not os.path.exists(file_path)):
    #         return []

    #     past_prices = file_reader.read_yaml(file_path)
    #     self.past_prices = past_prices['prices']

    #     self.logger.log_info(f'High: {mathematics.get_max(self.past_prices)}')
    #     self.logger.log_info(f'Median: {mathematics.get_median(self.past_prices)}')
    #     self.logger.log_info(f'Low: {mathematics.get_min(self.past_prices)}')

    def get_prices(self):
        file_path = os.path.join(DATA_DIRECTORY, 'prices.yml')
        if(not os.path.exists(file_path)):
            return []
        try:
            prices = file_reader.read_yaml(file_path)
            self.prices = prices['prices']
        except:
            self.prices = []

    def get_current_price(self):
        self.current_price = luno.get_price_ticker(self.trading_pair)
        self.logger.log_info(f'LUNO PRICE: {self.current_price}')
        self.prices.append(
            {
                'price': self.current_price,
                'timestamp': datetime.timestamp(datetime.now()),
                'trend': self.trend
            })

        self.update_trend()

        self._save_prices()

    def _get_purchase_value_from_orders(self, orders):
        value = 0.0
        for order in orders:
            quantity = float(order['quantity'])
            price = float(order['price'])
            value += quantity * price
        return value
