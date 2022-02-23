from datetime import datetime
from modules import file_reader, luno
from modules import luno, file_reader, mathematics, logger

DATA_FILE_NAME = 'past_funds'

class FundsManager:
    def __init__(self) -> None:
        self.past_funds = []
        self.funds = 0.0

    def update_funds(self):
        self.funds = self.get_funds()

    def get_funds(self):
        funds = float(luno.getSpendableBalance())
        self.logger_message.append(f'FUNDS: {funds}')
        return funds

    def save_past_funds(self):
        file_reader.write_data({DATA_FILE_NAME: self.past_funds}, DATA_FILE_NAME)

    def get_past_funds(self):
        data = file_reader.read_data(DATA_FILE_NAME)
        self.past_funds = data.get(DATA_FILE_NAME) or []

    def save_current_funds(self, orders):
        previous_funds = self.funds
        current_funds = self.get_funds()
        timestamp = datetime.timestamp(datetime.now())
        self.past_funds.append({DATA_FILE_NAME: previous_funds, 'current_funds': current_funds, 'timestamp': timestamp, 'orders': orders})
        self.save_past_funds()
