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
        self.profit_margin = config['profitMargin']
        self.trend_size = config['trendSize']
        self.trend_margin = config['trendMargin']
        self.min_trend_margin = config['minTrendMargin']
        self.purchase_trend_margin = config['purchaseTrendMargin']
        self.purchase_percentage = config['purchasePercent']
        self.min_trade_amount = config['minTradeAmount'][config['coin']]
        self.sell_range_margin = config['sellRangeMargin']
        self.buy_margin = config['buyMargin']
        self.pso_profit = config['psoProfit']
        self.cancel_count = config['cancelCount'] # Order cancel count
