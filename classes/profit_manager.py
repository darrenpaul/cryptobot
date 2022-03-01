from datetime import datetime
from modules import file_reader, mathematics


class ProfitManager:
    def __init__(self) -> None:
        self.past_profits = []

    def save_past_profits(self):
        file_reader.write_data({'past_profits': self.past_profits}, 'past_profits')

    def get_past_profits(self):
        data = file_reader.read_data('past_profits')
        self.past_profits = data.get('past_profits') or []

    def get_profit(self, complete_orders):
        profit = 0.0
        for order in complete_orders:
            side = order['side']
            if side == 'BUY':
                continue
            orders = order['orders']
            purchase_value = self._get_purchase_value_from_orders(orders)
            quantity = float(order['quantity'])
            price = float(order['price'])
            sell_value = quantity * price
            profit += sell_value - purchase_value

        self.logger_message.append(f'SELL PROFIT: {profit}')
        return profit
        
    def get_total_profit_old(self):
        profit = 0.0
        for order in self.past_orders:
            side = order['side']
            if side == 'BUY':
                continue
            orders = order['orders']
            purchase_value = self._get_purchase_value_from_orders(orders)
            quantity = float(order['quantity'])
            price = float(order['price'])
            sell_value = quantity * price
            profit += sell_value - purchase_value
        self.logger_message.append(f'CURRENT PROFIT: {profit}')

    def get_profits_for_day(self):
        today = datetime.today().date()
        profits = []
        for profit in self.past_profits:
            profit_date = datetime.fromtimestamp(profit['timestamp'])
            if profit_date.date() < today:
                continue
            profits.append(profit.get('profit'))
        return sum(profits)

    def get_total_profits_summary(self):
        total_profit = 0.0
        for profit in self.past_profits:
            if profit['profit'] is None:
                continue
            total_profit += float(profit['profit'])
        return total_profit

    def add_profit(self, profit):
        timestamp = datetime.timestamp(datetime.now())
        self.past_profits.append({'profit': profit, 'timestamp': timestamp})
        self.save_past_profits()
