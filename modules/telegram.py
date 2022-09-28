import json
import requests


class Telegram:
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, message):
        if self.chat_id and message:
            url = "https://api.telegram.org/bot{bot_token}/sendMessage".format(
                bot_token=self.bot_token
            )
            post_data = {"chat_id": self.chat_id, "text": message}
            return json.loads(requests.post(url, data=post_data).content)
