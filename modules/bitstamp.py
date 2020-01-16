BASE_URL = 'https://www.bitstamp.net/api/v2'
TICKER_URL = '{base_url}/ticker/'.format(base_url=BASE_URL)


def get_ticker(currency_pair):
    return TICKER_URL + currency_pair
