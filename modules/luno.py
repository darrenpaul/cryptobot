import time
import requests
import traceback
from requests.auth import HTTPBasicAuth


BASE_URL = 'https://api.luno.com/api/'
KEY_ID = 'bgdf4b6suu2es'
SECRET = 'oyDTcJ_RwQ8h1SxsvEDHxdfLZSV9JSeCbdEGBuhiaqc'
MAX_RETRY_COUNT = 3
RETRY_WAIT_TIME = 60


def do_get_request(url, params):
    retry_count = 0
    while True:
        try:
            response = requests.get(url, auth=HTTPBasicAuth(KEY_ID, SECRET), params=params)
            return response.json()
        except:
            time.sleep(RETRY_WAIT_TIME * retry_count)
            if retry_count == MAX_RETRY_COUNT:
                raise Exception('Max retry count reached')
            retry_count = retry_count + 1
            continue


def do_post_request(url, params):
    retry_count = 0
    while True:
        try:
            response = requests.post(url, auth=HTTPBasicAuth(KEY_ID, SECRET), params=params)
            return response.json()
        except:
            time.sleep(RETRY_WAIT_TIME)
            if retry_count == MAX_RETRY_COUNT:
                raise Exception('Max retry count reached')
            retry_count = retry_count + 1
            continue


def create_buy_order(pair, price, quantity, dry_run=False):
    if dry_run == True:
        return {'order_id': 'dry_run'}

    params = {
        'pair': pair,
        'type': 'BID',
        'price': price,
        'volume': quantity,
        'post_only': True
    }

    return do_post_request(f'{BASE_URL}1/postorder', params)


def create_sell_order(pair, price, quantity, dry_run=False):
    if dry_run == True:
        return {'id': 'dry_run'}

    params = {
        'pair': pair,
        'type': 'ASK',
        'price': price,
        'volume': quantity,
        'post_only': True
    }
    return do_post_request(f'{BASE_URL}1/postorder', params)


def list_orders(pair, state='PENDING'):
    params = {
        'pair': pair,
        'state': state
    }
    return do_get_request(f'{BASE_URL}1/listorders', params)


def close_open_order(order_id):
    params = {
        'order_id': order_id,
    }
    return do_post_request(f'{BASE_URL}1/stoporder', params)


def get_order(id):
    params = {'id': id}
    return do_get_request(f'{BASE_URL}exchange/3/order', params)


def get_price_ticker(pair):
    params = {'pair': pair}
    return float(do_get_request(f'{BASE_URL}1/tickers', params)['tickers'][0]['last_trade'])


def get_price_tickers():
    return do_get_request(f'{BASE_URL}1/tickers', {})['tickers']


def get_spendable_balance(currency='ZAR'):
    account_balance = get_account_balance(currency)['balance'][0]
    balance = float(account_balance.get('balance'))
    reserved = float(account_balance.get('reserved'))
    return float(balance - reserved)


def get_balance(currency='ZAR'):
    params = {'assets': currency}
    return do_get_request(f'{BASE_URL}1/balance', params)['balance'][0]['balance']


def get_account_balance(currency='ZAR'):
    params = {'assets': currency}
    return do_get_request(f'{BASE_URL}1/balance', params)


# # MAKE WORK
# def getReservedBalance(currency='ZAR'):
#     params = {'assets': currency}
#     return requests.get(f'{BASE_URL}1/balance', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params).json()['balance'][0]['balance']


# def get_pair_fee(pair):
#     params = {'pair': pair}
#     return requests.get(f'{BASE_URL}1/fee_info', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params).json()


# def close_open_orders(pair):
#     orders = list_orders(pair)
#     cancelled_orders = []

#     if not orders.get('orders'):
#         return cancelled_orders

#     for order in orders.get('orders'):
#         params = {
#             'order_id': order.get('order_id'),
#         }
#         result = requests.post(f'{BASE_URL}1/stoporder', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params)
#         cancelled_orders.append(result.json())

#     return cancelled_orders