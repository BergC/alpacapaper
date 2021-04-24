from os import environ
from pymongo import MongoClient

# Establish connection to Mongo Atlas
mongo_user_pw = environ['MONGO_USER_PASSWORD']
mongo_db_name = environ['MONGO_DB_NAME']

mongo_uri = f'mongodb+srv://cberg:{mongo_user_pw}@cluster0.2av1u.mongodb.net/{mongo_db_name}?retryWrites=true&w=majority'

client = MongoClient(mongo_uri)

db = client.polygon_tickers

# Historical date (YYYY-MM-DD) to get ticker data for.
today = '2021-04-21'

existing_companies = db[today]

print(existing_companies.count_documents({ 'ticker': 'ZBRA' }, limit = 1))

# if existing_companies.count_documents({ 'ticker': 'ZBRA' }, limit = 1) != 0:
#     print('Exists')
