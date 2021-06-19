import requests
from os import environ
from datetime import datetime, timedelta
import time
from pymongo import MongoClient

# Today's date used to query today's Polygon data.
# today = str(datetime.today().strftime('%Y-%m-%d'))
today = '2021-06-10'

# Mongo Environment Variables.
mongo_user_pw = environ['MONGO_USER_PASSWORD']
polygon_db_name = environ['MONGO_DB_POLYGON']
alpha_db_name = environ['MONGO_DB_ALPHA']

# Polygon MongoDB connection.
polygon_mongo_uri = f'mongodb+srv://cberg:{mongo_user_pw}@cluster0.2av1u.mongodb.net/{polygon_db_name}?retryWrites=true&w=majority'

polygon_client = MongoClient(polygon_mongo_uri)

polygon_db = polygon_client.polygon_tickers

# Alpha Vantage MongoDB connection.
alpha_mongo_uri = f'mongodb+srv://cberg:{mongo_user_pw}@cluster0.2av1u.mongodb.net/{alpha_db_name}?retryWrites=true&w=majority'

alpha_client = MongoClient(alpha_mongo_uri)

alpha_db = alpha_client.alpha_vantage

# Tickers used to collect fundamentals for.
today_tickers = polygon_db.qualified_tickers.find()
today_tickers_list = [x for x in today_tickers]
today_count = polygon_db.qualified_tickers.estimated_document_count()

# Alpha Vantage's API core endpoint.
url = 'https://www.alphavantage.co/query?'

# Alpha Vantage's free API limits to 5 calls per minute.
# Use this variable to track our total per minute and pause when needed.
num_calls = 0

# Hit Alpha's API for each Ticker that met our momentum criteria from Polygon.
for ticker in today_tickers_list:
    try:
        # Puts script to sleep after 5 calls so we don't exceed Alpha's free tier limit.
        if num_calls != 0 and num_calls % 5 == 0:
            num_remaining = today_count - num_calls
            print(f'Sleeping, {num_calls} ADXs completed so far. We have {num_remaining} tickers left.')

            time.sleep(65)

        payload = {
            'function': 'ADX',
            'symbol': ticker['ticker'],
            'interval': 'daily',
            'time_period': 60,
            'apikey': environ['ALPHA_API_KEY_1']
        }

        r = requests.get(url, params=payload)

        r_json = r.json()

        if 'Error Message' in r_json or r_json is False or r_json == {}:
            num_calls += 1
            continue

        # Sometimes fundamental data doesn't exist for given ticker so we check if
        # the dictionary is populated. Returns Falsy if the dictionary is empty.
        if r_json['Technical Analysis: ADX']:
            adx = float(r_json['Technical Analysis: ADX'][today]['ADX'])

            # Push buy sign cross overs below the zero line to their own collection.
            if adx > 30:
                alpha_db['adx_test'].insert_one({
                    'ticker': ticker['ticker'],
                    'open': ticker['open'],
                    'close': ticker['close'],
                    'high': ticker['high'],
                    'low': ticker['low'],
                    'fundamentals': {
                        'adx': adx
                    }
                })

            num_calls += 1
    except KeyError:
        print(num_calls)
        print(ticker['ticker'])
        num_calls += 1
        continue
