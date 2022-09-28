from modules import luno


class FundsManager:
    def __init__(self) -> None:
        self.funds = 0.0

    def update_funds(self):
        self.funds = self.get_funds()

    def get_funds(self):
        funds = float(luno.get_spendable_balance())
        self.logger.log_info(f"FUNDS: {funds}")
        return funds
