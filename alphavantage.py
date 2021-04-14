import requests
import os
from datetime import datetime, timedelta
import time
from pymongo import MongoClient

# Today's date used to query today's Polygon data.
# today = str(datetime.today().strftime('%Y-%m-%d'))
today = '2021-04-13'

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

# Create two new collections to contain tickers with MACD cross overs above
# and below the zero line.
alpha_db[today].insert_one({
    'id': 'buy_below_zero',
    'tickers': []
})

alpha_db[today].insert_one({
    'id': 'buy_above_zero',
    'tickers': []
})

# Tickers used to collect fundamentals for.
today_tickers = polygon_db[today].find()
today_count = polygon_db[today].estimated_document_count()

# Alpha Vantage's API core endpoint.
url = 'https://www.alphavantage.co/query?'

# Alpha Vantage's free API limits to 5 calls per minute.
# Use this variable to track our total per minute and pause when needed.
num_calls = 0

# Hit Alpha's API for each Ticker that met our momentum criteria from Polygon.
for ticker in today_tickers:
    # Puts script to sleep after 5 calls so we don't exceed Alpha's free tier limit.
    if num_calls != 0 and num_calls % 5 == 0:
        num_remaining = today_count - num_calls
        print(f'Sleeping, {num_calls} completed so far. We have {num_remaining} tickers left.')
        time.sleep(61)

    payload = {
        'function': 'MACD',
        'symbol': ticker['ticker'],
        'interval': 'daily',
        'series_type': 'close',
        'apikey': os.environ['ALPHA_API_KEY']
    }

    r = requests.get(url, params=payload)

    r_json = r.json()

    # Sometimes fundamental data doesn't exist for given ticker so we check if
    # the dictionary is populated. Returns Falsy if the dictionary is empty.
    if r_json['Technical Analysis: MACD']:
        macd_dic = r_json['Technical Analysis: MACD']
        macd_nums = r_json['Technical Analysis: MACD'][today]

        # Push buy sign cross overs below the zero line to their own document.
        if float(macd_nums['MACD']) > float(macd_nums['MACD_Signal']) and float(macd_nums['MACD']) < 0 and float(macd_nums['MACD_Signal']) < 0:
            alpha_db[f'{today}'].update_one({'id': 'buy_below_zero'}, { '$push': { 'tickers' : {
                'ticker': ticker['ticker'],
                'open': ticker['open'],
                'close': ticker['close'],
                'high': ticker['high'],
                'low': ticker['low'],
                'fundamentals': {
                    'MACD': {
                        'MACD': macd_nums['MACD'],
                        'MACD_Signal': macd_nums['MACD_Signal'],
                        'MACD_Hist': macd_nums['MACD_Hist']
                    }
                }
            }}})

        # Push buy sign cross overs above the zero line to a separate document.
        elif float(macd_nums['MACD']) > float(macd_nums['MACD_Signal']):
            alpha_db[f'{today}'].update_one({'id': 'buy_above_zero'}, {'$push': {'tickers': {
                'ticker': ticker['ticker'],
                'open': ticker['open'],
                'close': ticker['close'],
                'high': ticker['high'],
                'low': ticker['low'],
                'fundamentals': {
                    'MACD': {
                        'MACD': macd_nums['MACD'],
                        'MACD_Signal': macd_nums['MACD_Signal'],
                        'MACD_Hist': macd_nums['MACD_Hist']
                    }
                }
            }}})

    num_calls += 1
