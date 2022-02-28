from datetime import datetime
from modules import file_reader, mathematics


class TrendManager:
    def __init__(self) -> None:
        self.trend_size = 10
        self.down_trend_margin_start = 100
        self.down_trend_margin_end = 90
        self.up_trend_margin_start = 100
        self.up_trend_margin_end = 90
        self.trend = 100.0
        self.past_trends = []

    def save_past_trends(self):
        file_reader.write_data({'past_trends': self.past_trends}, 'past_trends')

    def get_past_trends(self):
        data = file_reader.read_data('past_trends')
        self.past_trends = data.get('past_trends') or []

    def update_trend(self, current_price):
            trend_price = mathematics.get_trend(self.past_prices, self.trend_size)
            self.trend = mathematics.round_up(trend_price)

            self.logger_message.append(f'TREND: {self.trend}')

            timestamp = datetime.timestamp(datetime.now())

            self.past_trends.append({
                'trend': self.trend,
                'timestamp': timestamp,
                'price': current_price,
            })
            self.save_past_trends()

    def check_if_trend_in_range(self):
        if self.trend >= self.down_trend_margin_end and self.trend <= self.up_trend_margin_end:
            if self.trend <= self.down_trend_margin_start or self.trend >= self.up_trend_margin_start:
                return True
        return False

