import os
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from pymongo import MongoClient

# Import MongoDB credentials.
mongo_pw = os.environ['MONGO_USER_PASSWORD']
mongo_db = os.environ['MONGO_DB_NAME']

# Connect to our db.
mongo_uri = f'mongodb+srv://cberg:{mongo_pw}@cluster0.2av1u.mongodb.net/{mongo_db}?retryWrites=true&w=majority'

client = MongoClient(mongo_uri)

db = client.alpha_vantage

# Import our Alpaca API keys.
APCA_API_KEY_ID = os.environ['APCA_API_KEY_ID']
APCA_API_SECRET_KEY = os.environ['APCA_API_SECRET_KEY']
APCA_API_BASE_URL = os.environ['APCA_API_BASE_URL']

# Establish RESTful connection with Alpaca's API using our keys.
api = tradeapi.REST(
    APCA_API_KEY_ID,
    APCA_API_SECRET_KEY,
    APCA_API_BASE_URL
)

# # Check if market is open.
# clock = api.get_clock()
# is_open = clock.is_open
#
# if is_open == False:
#     exit()

# Today's date used to query today's Polygon data.
today = str(datetime.today().strftime('%Y-%m-%d'))

# Get stocks to buy.
below_zero_crossovers = db[f'{today}: Below Zero'].find()

print(api.get_account())

def qty_per_ticker(share_price):
    '''

    :param share_price:
    :return:
    '''

    base = 100000

    account = api.get_account()
    current_cash = account.cash

    maximum_exposure = 0.02

    num_shares = round((base * maximum_exposure) / share_price)

    return num_shares

for ticker in below_zero_crossovers:
    if ticker['fundamentals']['rsi']:
        api.submit_order(
            ticker['ticker'],
            qty_per_ticker(ticker['close']),
            'buy',
            'market',
            'day'
        )
