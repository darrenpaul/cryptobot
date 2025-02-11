import time
import requests
import traceback
from requests.auth import HTTPBasicAuth

from modules import logger


BASE_URL = "https://www.bitstamp.net/api/v2/"
MAX_RETRY_COUNT = 3
RETRY_WAIT_TIME = 60


def do_get_request(url):
    retry_count = 0
    while True:
        try:
            response = requests.get(url)
            return response.json()
        except:
            time.sleep(RETRY_WAIT_TIME * retry_count)
            f"Error: {traceback.format_exc()}"
            if retry_count == MAX_RETRY_COUNT:
                raise Exception("Max retry count reached")
            retry_count = retry_count + 1
            continue


def get_price_ticker(pair):
    return float(do_get_request(f"{BASE_URL}ticker/{pair}")["last"])
