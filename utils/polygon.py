import requests
import os
from datetime import datetime
from pymongo import MongoClient

# Establish connection to Mongo Atlas
mongo_user_pw = os.environ['MONGO_USER_PASSWORD']
mongo_db_name = os.environ['MONGO_DB_NAME']

mongo_uri = f'mongodb+srv://cberg:{mongo_user_pw}@cluster0.2av1u.mongodb.net/{mongo_db_name}?retryWrites=true&w=majority'

client = MongoClient(mongo_uri)

db = client.polygon_tickers

# Historical date (YYYY-MM-DD) to get ticker data for.
today = str(datetime.today().strftime('%Y-%m-%d'))
# today = '2021-04-21'

# Polygon API endpoint payload.
payload = {
    'unadjusted': 'true',
    'apiKey': os.environ['POLYGON_API_KEY']
}

# API endpoint for all US stock ticker symbols.
url = f'https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{today}?'

r = requests.get(url, params=payload)

# Check if Polygon's API returns status 200.
if r.status_code != 200:
    print(f'GET request returned a status {r.status_code}')
    exit()

r_to_json = r.json()


def is_already_saved(symbol):
    """
    Determine if the provided sticker symbol already exists in the database.
    :param symbol: String -> Company ticker symbol
    :return: True if ticker already exists in database
    """

    return True if db.qualified_tickers.count_documents({'ticker': symbol}, limit=1) == 1 else False


# Save tickers trading at >$5 with a dollar volume greater than $20M that aren't already saved.
for ticker in r_to_json['results']:
    dollar_volume = ticker['v'] * ticker['c']
    stock_price = ticker['c']
    curr_ticker = ticker['T']

    if dollar_volume > 20000000 and stock_price > 5 and is_already_saved(curr_ticker) is False:
        db['qualified_tickers'].insert_one(
            {
                'ticker': curr_ticker,
                'open': ticker['o'],
                'close': ticker['c'],
                'high': ticker['h'],
                'low': ticker['l']
            }
        )
    elif is_already_saved(curr_ticker) is True and (dollar_volume < 20000000 or stock_price < 5):
        db['qualified_tickers'].delete_one(
            {
                'ticker': curr_ticker
            }
        )
