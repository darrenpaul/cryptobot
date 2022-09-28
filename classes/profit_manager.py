from datetime import datetime, timedelta
from modules import file_reader, mathematics


class ProfitManager:
    def __init__(self) -> None:
        self.past_profits = []

    def save_past_profits(self):
        file_reader.write_data({"past_profits": self.past_profits}, "past_profits")

    def get_past_profits(self):
        data = file_reader.read_data("past_profits")
        self.past_profits = data.get("past_profits") or []

    def get_profit(self, complete_orders):
        profit = 0.0
        for order in complete_orders:
            side = order["side"]
            if side == "BUY":
                continue
            orders = order["orders"]
            purchase_value = self._get_purchase_value_from_orders(orders)
            quantity = float(order["quantity"])
            price = float(order["price"])
            sell_value = quantity * price
            profit += sell_value - purchase_value

        self.logger.log_info(f"SELL PROFIT: {profit}")
        return profit

    def get_total_profit_old(self):
        profit = 0.0
        for order in self.past_orders:
            side = order["side"]
            if side == "BUY":
                continue
            orders = order["orders"]
            purchase_value = self._get_purchase_value_from_orders(orders)
            quantity = float(order["quantity"])
            price = float(order["price"])
            sell_value = quantity * price
            profit += sell_value - purchase_value
        self.logger.log_info(f"CURRENT PROFIT: {profit}")

    def get_profits_for_day(self):
        today = datetime.today().date()
        profits = []
        for profit in self.past_profits:
            profit_date = datetime.fromtimestamp(profit["timestamp"])
            if profit_date.date() < today:
                continue
            profits.append(profit.get("profit"))
        return sum(profits)

    def get_profits_for_week(self):
        today = datetime.today()
        start_week = today - timedelta(today.weekday())

        profits = []
        for profit in self.past_profits:
            profit_date = datetime.fromtimestamp(profit["timestamp"])
            if profit_date.date() < start_week.date():
                continue
            profits.append(profit.get("profit"))
        return sum(profits)

    def get_profits_for_month(self):
        today = datetime.today()

        profits = []
        for profit in self.past_profits:
            profit_date = datetime.fromtimestamp(profit["timestamp"])
            if profit_date.date().month != today.date().month:
                continue
            profits.append(profit.get("profit"))

        return sum(profits)

    def get_profits_for_year(self):
        today = datetime.today()

        profits = []
        for profit in self.past_profits:
            profit_date = datetime.fromtimestamp(profit["timestamp"])
            if profit_date.date().year != today.date().year:
                continue
            profits.append(profit.get("profit"))

        return sum(profits)

    def get_total_profits_summary(self):
        total_profit = 0.0
        for profit in self.past_profits:
            if profit["profit"] is None:
                continue
            total_profit += float(profit["profit"])
        return total_profit

    def add_profit(self, profit):
        timestamp = datetime.timestamp(datetime.now())
        self.past_profits.append({"profit": profit, "timestamp": timestamp})
        self.save_past_profits()

    def increase_profit_amount(self):
        self.logger.log_info(f"============================")
        self.logger.log_info(f"=== INCREASING BUY ORDER PRICES ===")
        self.logger.log_info(f"============================")
        increase_amount = 0.01
        for order in self.bought_orders:
            if not order.get("increase_profit_count"):
                continue

            order["increase_profit_count"] = order["increase_profit_count"] + 1

            if order["increase_profit_count"] >= 3:
                order["limit_price"] = float(order["limit_price"]) + float(
                    increase_amount
                )
                order["increase_profit_count"] = 0
        self.save_order(self.bought_orders, "buy")
