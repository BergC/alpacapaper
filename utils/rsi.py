import requests
import os
from datetime import datetime, timedelta
import time
from pymongo import MongoClient

# Today's date used to query today's Polygon data.
today = str(datetime.today().strftime('%Y-%m-%d'))

# Connect to MongoDB
mongo_user_pw = os.environ['MONGO_USER_PASSWORD']
db_name = os.environ['MONGO_DB_NAME']

mongo_uri = f'mongodb+srv://cberg:{mongo_user_pw}@cluster0.2av1u.mongodb.net/{db_name}?retryWrites=true&w=majority'

client = MongoClient(mongo_uri)

db = client.alpha_vantage

ticker_count = db[today].estimated_document_count()

# Collect the RSI candidates based on tickers with MACD crossovers below zero line.
below_zero_crossovers = db[today].find()
below_zero_crossovers_list = [x for x in below_zero_crossovers]

# Alpha Vantage's API core endpoint.
url = 'https://www.alphavantage.co/query?'

# Alpha Vantage's free API limits to 5 calls per minute.
# Use this variable to track our total per minute and pause when needed.
num_rsi_calls = 0


def rsi(date):
    """
    Helper function to return today's RSI
    :param date: String formatted date eg. 2021-04-14
    :return: Float value of the RSI for given date
    """

    # print(float(r_json['Technical Analysis: RSI'][date]['RSI']))
    return float(r_json['Technical Analysis: RSI'][date]['RSI'])


def rsi_prior(lookback):
    """
    Similar to rsi function but x number of days in the past.
    :param lookback: Number of days the date should be reduced by.
    :return: Float value of the RSI for given date.
    """

    lookback_date = (datetime.today() - timedelta(lookback))
    day_of_week = lookback_date.weekday()

    if day_of_week <= 4:
        lookback_date_str = str(lookback_date.strftime('%Y-%m-%d'))

        return float(r_json['Technical Analysis: RSI'][lookback_date_str]['RSI'])
    elif day_of_week == 5:
        lookback_date = (datetime.today() - timedelta(lookback + 3)).strftime('%Y-%m-%d')
        lookback_date_str = str(lookback_date)

        return float(r_json['Technical Analysis: RSI'][lookback_date_str]['RSI'])

    lookback_date = (datetime.today() - timedelta(lookback + 2)).strftime('%Y-%m-%d')
    lookback_date_str = str(lookback_date)

    return float(r_json['Technical Analysis: RSI'][lookback_date_str]['RSI'])


for ticker in below_zero_crossovers:
    # Puts script to sleep after 5 calls so we don't exceed Alpha's free tier limit.
    if num_rsi_calls != 0 and num_rsi_calls % 5 == 0:
        num_remaining = ticker_count - num_rsi_calls
        print(f'Sleeping, {num_rsi_calls} RSIs completed so far. We have {num_remaining} tickers left.')
        time.sleep(61)

    payload = {
        'function': 'RSI',
        'symbol': ticker['ticker'],
        'interval': 'daily',
        'series_type': 'close',
        'time_period': 14,
        'apikey': os.environ['ALPHA_API_KEY']
    }

    r = requests.get(url, params=payload)

    r_json = r.json()

    if r_json['Technical Analysis: RSI'] and rsi(today) > 30 and rsi(today) > rsi_prior(1) and rsi_prior(1) > rsi_prior(2):
        db[today].update_one(
            {
                'ticker': ticker['ticker']
            },
            {
                '$set': {
                    'fundamentals.rsi': rsi(today)
                }
            }
        )

    num_rsi_calls += 1
