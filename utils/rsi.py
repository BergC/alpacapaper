import requests
import os
from datetime import datetime, timedelta
import time
from pymongo import MongoClient

# Today's date used to query today's Polygon data.
today = str(datetime.today().strftime('%Y-%m-%d'))
# today = '2021-06-04'

# Connect to MongoDB
mongo_user_pw = os.environ['MONGO_USER_PASSWORD']
db_name = os.environ['MONGO_DB_NAME']

mongo_uri = f'mongodb+srv://cberg:{mongo_user_pw}@cluster0.2av1u.mongodb.net/{db_name}?retryWrites=true&w=majority'

client = MongoClient(mongo_uri)

db = client.alpha_vantage

ticker_count = db[today].estimated_document_count()

# Collect the RSI candidates based on tickers with MACD crossovers below zero line.
qualified_tickers = db[today].find()

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


def rsi_trend_positive(rsi_dict):
    """
    Assess the trend of the RSI.
    RSI over 30 is considered good, but if the RSI is downward trending towards 30 that's bad.
    :param rsi_dict:
    :return:
    """

    rsi_iterable = list(rsi_dict.items())

    # Only looking at the last 10 days of data.
    test_batch = [float(x[1]['RSI']) for x in rsi_iterable[0:10]]

    if sum(test_batch) / len(test_batch) < test_batch[0]:
        return True

    return False


for ticker in qualified_tickers:
    # Puts script to sleep after 5 calls so we don't exceed Alpha's free tier limit.
    if num_rsi_calls != 0 and num_rsi_calls % 5 == 0:
        num_remaining = ticker_count - num_rsi_calls
        print(f'Sleeping, {num_rsi_calls} RSIs completed so far. We have {num_remaining} tickers left.')
        time.sleep(65)

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

    curr_ticker_rsi = r_json['Technical Analysis: RSI']

    rsi_trend_positive(curr_ticker_rsi)

    if curr_ticker_rsi and rsi(today) > 50 and rsi_trend_positive(curr_ticker_rsi) is True:
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
    else:
        db[today].delete_one(
            {
                'ticker': ticker['ticker']
            }
        )

    num_rsi_calls += 1
