from datetime import datetime
from modules import file_reader, mathematics


class TrendManager:
    def __init__(self) -> None:
        self.trend_size = 10
        self.trend_margin = 100
        self.min_trend_margin = 90
        self.purchase_trend_margin = 90
        self.trend = 100
        self.purchase_trend = 100
        self.past_trends = []

    def save_past_trends(self):
        file_reader.write_data({'past_trends': self.past_trends}, 'past_trends')

    def get_past_trends(self):
        data = file_reader.read_data('past_trends')
        self.past_trends = data.get('past_trends') or []

    def update_trend(self, average_price, current_price):
            self.trend = round(mathematics.get_trend(self.past_prices, self.trend_size, int(self.trend_size / 2)), 2)
            self.purchase_trend = round(mathematics.get_trend([average_price, current_price], 2, 1), 2)
            self.logger_message.append(f'TREND: {self.trend}')
            self.logger_message.append(f'PURCHASE TREND: {self.purchase_trend}')
            timestamp = datetime.timestamp(datetime.now())
            self.past_trends.append({'trend': self.trend, 'timestamp': timestamp, 'price': current_price, 'purchase_trend': self.purchase_trend})
            self.save_past_trends()