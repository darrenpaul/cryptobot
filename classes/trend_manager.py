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

    def update_trend(self, current_price):
        trend_price = mathematics.get_trend(self.past_prices, self.trend_size)
        self.trend = mathematics.round_up(trend_price)

        self.log_info(f'TREND: {self.trend}')

    def check_if_trend_in_range(self):
        if self.trend >= self.down_trend_margin_end and self.trend <= self.up_trend_margin_end:
            if self.trend <= self.down_trend_margin_start or self.trend >= self.up_trend_margin_start:
                return True
        return False

