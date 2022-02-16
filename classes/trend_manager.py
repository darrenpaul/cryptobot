import os
import time

from pathlib import Path
from datetime import datetime
from modules import luno, file_reader, mathematics, logger
from classes import buy_manager, sell_manager, price_manager


class TrendManager:
    def __init__(self) -> None:
        self.trend_size = 10
        self.trend_margin = 100
        self.min_trend_margin = 90
        self.trend = 100
        self.past_trends = []

    def save_past_trends(self):
        file_reader.write_data({'past_trends': self.past_trends}, 'past_trends')

    def get_past_trends(self):
        data = file_reader.read_data('past_trends')
        self.past_trends = data.get('past_trends') or []

    def update_trend(self, price):
            self.trend = mathematics.get_trend(self.past_prices, self.trend_size, int(self.trend_size / 2))
            self.logger_message.append(f'TREND: {self.trend}')
            timestamp = datetime.timestamp(datetime.now())
            self.past_trends.append({'trend': self.trend, 'timestamp': timestamp, 'price': price})
            self.save_past_trends()