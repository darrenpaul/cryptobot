import os
from pathlib import Path
from modules import file_reader


class ConfigManager:
    def __init__(self):
        pass

    def get_config(self):
        file_path = os.path.join(Path(__file__).parent, 'config.yml')
        config = file_reader.read_yaml(file_path)
        self.coin = config["coin"]
        self.trading_pair = f'{config["coin"]}{config["currency"]}'
        self.profit_percentage = config['profitPercentage']
        self.trend_size = config['trendSize']
        self.down_trend_margin_start = config['downTrendMarginStart']
        self.down_trend_margin_end = config['downTrendMarginEnd']
        self.up_trend_margin_start = config['upTrendMarginStart']
        self.up_trend_margin_end = config['upTrendMarginEnd']
        self.purchase_percentage = config['purchasePercent']
        self.min_trade_amount = config['minTradeAmount'][config['coin']]
        self.sell_group_margin = config['sellGroupMargin']
        self.buy_margin = config['buyMargin']
        self.cancel_count = config['cancelCount'] # Order cancel count
        self.buy_price_margin = config['buyPriceMargin']
