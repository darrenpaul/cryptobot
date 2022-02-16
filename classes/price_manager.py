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

        print(f'High: {mathematics.get_max(self.past_prices)}')
        print(f'Median: {mathematics.get_median(self.past_prices)}')
        print(f'Low: {mathematics.get_min(self.past_prices)}')

    def get_current_price(self):
        current_price = luno.getPriceTicker(self.trading_pair)
        self.past_prices.append(current_price)
        self._save_prices()
        print(f'Current Market Price: {current_price}')
        return current_price