import os

from pathlib import Path
from modules import luno, file_reader, mathematics


DATA_DIRECTORY =  os.path.join(Path(__file__).parent.parent, 'data')


class PriceManager:
    def __init__(self) -> None:
        self.past_prices = []

    def _save_prices(self):
        file_path = os.path.join(DATA_DIRECTORY, 'past_prices.yml')
        data = {'prices': self.past_prices}
        file_reader.write_yaml(data, file_path)

    def get_past_prices(self):
        file_path = os.path.join(DATA_DIRECTORY, 'past_prices.yml')
        if(not os.path.exists(file_path)):
            return []

        past_prices = file_reader.read_yaml(file_path)
        self.past_prices = past_prices['prices']

        self.logger_message.append(f'High: {mathematics.get_max(self.past_prices)}')
        self.logger_message.append(f'Median: {mathematics.get_median(self.past_prices)}')
        self.logger_message.append(f'Low: {mathematics.get_min(self.past_prices)}')

    def get_current_price(self):
        current_price = luno.getPriceTicker(self.trading_pair)
        self.logger_message.append(f'CURRENT PRICE: {current_price}')
        self.past_prices.append(current_price)
        self._save_prices()
        return current_price