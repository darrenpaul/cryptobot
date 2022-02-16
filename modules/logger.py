import os
import logging

from pathlib import Path

DATA_DIRECTORY = os.path.join(Path(__file__).parent.parent, 'data')
FILE_PATH = os.path.join(DATA_DIRECTORY, 'logs.txt')
FORMAT_SYMBOL = '*'
FORMAT_AMOUNT = 40

class BotLogger:
    def __init__(self):
        self.module_logger = logging.getLogger('CrytoBot')

        level = logging.basicConfig(level=logging.DEBUG)
        formatting = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(formatting)
        
        file_handler = logging.FileHandler(FILE_PATH)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatting)

        self.module_logger.addHandler(stdout_handler)
        self.module_logger.addHandler(file_handler)

    def log_info(self, message):
        self.module_logger.info(message)

    def log_warning(self, message):
        self.module_logger.warning(message)

    def log_info_message(self, message):
        self.log_info(FORMAT_SYMBOL * FORMAT_AMOUNT)
        self.log_info('\n'.join(message))
        self.log_info(FORMAT_SYMBOL * FORMAT_AMOUNT)