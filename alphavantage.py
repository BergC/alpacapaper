import requests
import os
from datetime import datetime
import time
from pymongo import MongoClient

# Mongo Environment Variables.
mongo_user_pw = os.environ['MONGO_USER_PASSWORD']
polygon_db_name = os.environ['MONGO_DB_POLYGON']
alpha_db_name = os.environ['MONGO_DB_ALPHA']

# Polygon MongoDB connection.
polygon_mongo_uri = f'mongodb+srv://cberg:{mongo_user_pw}@cluster0.2av1u.mongodb.net/{polygon_db_name}?retryWrites=true&w=majority'

polygon_client = MongoClient(polygon_mongo_uri)

polygon_db = polygon_client.polygon_tickers

# Alpha Vantage MongoDB connection.
alpha_mongo_uri = f'mongodb+srv://cberg:{mongo_user_pw}@cluster0.2av1u.mongodb.net/{alpha_db_name}?retryWrites=true&w=majority'

alpha_client = MongoClient(alpha_mongo_uri)

alpha_db = alpha_client.alpha_vantage

# Today's date used to query today's Polygon data.
today = str(datetime.today().strftime('%Y-%m-%d'))

# RSI, MACD, RSI
today_tickers = polygon_db[today].find_one({'id': today})['data']
today_count = polygon_db[today].find_one({'id': today})['count']

url = 'https://www.alphavantage.co/query?'

# Alpha Vantage's free API limits to 5 calls per minute.
# Use this variable to track our running total and pause when needed.
num_calls = 0

# Hit Alpha's API for each Ticker that met our momentum criteria from Polygon.
for ticker in today_tickers:
    if num_calls != 0 and num_calls % 5 == 0:
        print('sleeping')
        time.sleep(61)

    payload = {
        'function': 'MACD',
        'symbol': ticker['ticker'],
        'interval': 'daily',
        'series_type': 'close',
        'apikey': os.environ['ALPHA_VANTAGE_API_KEY']
    }

    r = requests.get(url, params=payload)

    r_json = r.json()

    if float(r_json['Technical Analysis: MACD'][today]['MACD_Signal']) > 0:
        alpha_db[today].insert_one({
            'ticker': ticker['ticker'],
            'open': ticker['open'],
            'close': ticker['close'],
            'high': ticker['high'],
            'low': ticker['low'],
            'fundamentals': {
                'macd': float(r_json['Technical Analysis: MACD'][today]['MACD_Signal'])
            }
        })

    num_calls += 1
