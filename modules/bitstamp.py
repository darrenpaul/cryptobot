import requests


BASE_URL = 'https://www.bitstamp.net/api/v2'
TICKER_URL = '{base_url}/ticker/'.format(base_url=BASE_URL)


def get_latest_ticker(currency_pair):
    url = TICKER_URL + currency_pair
    result = requests.get(url)
    if not result:
        return False
    if not result.status_code == 200:
        return False
    return result.json()

