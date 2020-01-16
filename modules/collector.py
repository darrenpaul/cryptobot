import requests
from pprint import pprint
from . import bitstamp


def latest_ticker(currency_pair):
    url = bitstamp.get_ticker(currency_pair)
    result = requests.get(url)
    if not result:
        return False
    if not result.status_code == 200:
        return False
    return result.json()
