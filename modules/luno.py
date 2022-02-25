from numpy import append
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = 'https://api.luno.com/api/'
KEY_ID = 'bgdf4b6suu2es'
SECRET = 'oyDTcJ_RwQ8h1SxsvEDHxdfLZSV9JSeCbdEGBuhiaqc'


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
    return requests.post(f'{BASE_URL}1/postorder', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params).json()


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
    return requests.post(f'{BASE_URL}1/postorder', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params).json()


def list_orders(pair, state='PENDING'):
    params = {
        'pair': pair,
        'state': state
    }
    return requests.get(f'{BASE_URL}1/listorders', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params).json()


def close_open_orders(pair):
    orders = list_orders(pair)
    cancelled_orders = []

    if not orders.get('orders'):
        return cancelled_orders

    for order in orders.get('orders'):
        params = {
            'order_id': order.get('order_id'),
        }
        result = requests.post(f'{BASE_URL}1/stoporder', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params)
        cancelled_orders.append(result.json())

    return cancelled_orders


def close_open_order(order_id):
    params = {
        'order_id': order_id,
    }
    return requests.post(f'{BASE_URL}1/stoporder', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params)


def get_order(id):
    params = {'id': id}
    return requests.get(f'{BASE_URL}exchange/3/order', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params).json()


def getPriceTicker(pair):
    params = {'pair': pair}
    return float(requests.get(f'{BASE_URL}1/tickers', params=params).json()['tickers'][0]['last_trade'])


def getPriceTickers():
    return requests.get(f'{BASE_URL}1/tickers').json()


def getSpendableBalance(currency='ZAR'):
    account_balance = getAccountBalance(currency)['balance'][0]
    balance = float(account_balance.get('balance'))
    reserved = float(account_balance.get('reserved'))
    return float(balance - reserved)


# MAKE WORK
def getBalance(currency='ZAR'):
    params = {'assets': currency}
    return requests.get(f'{BASE_URL}1/balance', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params).json()['balance'][0]['balance']

# MAKE WORK
def getReservedBalance(currency='ZAR'):
    params = {'assets': currency}
    return requests.get(f'{BASE_URL}1/balance', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params).json()['balance'][0]['balance']


def getAccountBalance(currency='ZAR'):
    params = {'assets': currency}
    return requests.get(f'{BASE_URL}1/balance', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params).json()


def getPairFee(pair):
    params = {'pair': pair}
    return requests.get(f'{BASE_URL}1/fee_info', auth=HTTPBasicAuth(KEY_ID, SECRET), params=params).json()
