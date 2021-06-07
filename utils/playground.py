from os import environ
import requests
from pymongo import MongoClient

# # Establish connection to Mongo Atlas
# mongo_user_pw = environ['MONGO_USER_PASSWORD']
# mongo_db_name = environ['MONGO_DB_NAME']
#
# mongo_uri = f'mongodb+srv://cberg:{mongo_user_pw}@cluster0.2av1u.mongodb.net/{mongo_db_name}?retryWrites=true&w=majority'
#
# client = MongoClient(mongo_uri)
#
# db = client.polygon_tickers
#
# # Historical date (YYYY-MM-DD) to get ticker data for.
# today = '2021-04-21'
#
# existing_companies = db[today]
#
# print(existing_companies.count_documents({ 'ticker': 'ZBRA' }, limit = 1))
#
# # if existing_companies.count_documents({ 'ticker': 'ZBRA' }, limit = 1) != 0:
# #     print('Exists')

# def alpha_api_key(curr_calls):
#     """
#
#     :param curr_calls:
#     :return:
#     """
#
#     alpha_keys = [
#         'ALPHA_API_KEY_1',
#         'ALPHA_API_KEY_2',
#         'ALPHA_API_KEY_3',
#         'ALPHA_API_KEY_4',
#         'ALPHA_API_KEY_5',
#         'ALPHA_API_KEY_6'
#     ]
#
#     alpha_keys_index = int((curr_calls / 5) - 1)
#
#     return environ[alpha_keys[alpha_keys_index]]

# num_calls = 0
#
# alpha_keys = [
#     'ALPHA_API_KEY_1',
#     'ALPHA_API_KEY_2',
#     'ALPHA_API_KEY_3',
#     'ALPHA_API_KEY_4',
#     'ALPHA_API_KEY_5',
#     'ALPHA_API_KEY_6'
# ]
#
# for key in alpha_keys:
#     if num_calls == 3:
#         num_calls = 1
#     else:
#         num_calls += 1
#
#     print(num_calls)

# def round_down(num, divisor):
#     return num - (num % divisor)
#
# print(round_down(30, 5))

url = 'https://www.alphavantage.co/query?'

payload = {
    'function': 'RSI',
    'symbol': 'CHWY',
    'interval': 'daily',
    'series_type': 'close',
    'time_period': 14,
    'apikey': environ['ALPHA_API_KEY']
}

r = requests.get(url, params=payload)

r_json = r.json()

curr_ticker_rsi = r_json['Technical Analysis: RSI']

# print(curr_ticker_rsi)

def rsi_trend_positive(rsi_dict):
    """

    :param rsi_dict:
    :return:
    """
    what = []

    for dict in rsi_dict:
        key = next(iter(rsi_dict))
        huh = dict[key]['RSI']
        what.append(huh)

    print(what)

rsi_trend_positive(curr_ticker_rsi)

