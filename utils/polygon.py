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

# Polygon API endpoint payload.
payload = {
    'unadjusted': 'true',
    'apiKey': os.environ['POLYGON_API_KEY']
}

# API endpoint for all US stock ticker symbols.
url = f'https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{today}?'

r = requests.get(url, params=payload)

# Check if Polygon's API returns status 200.
if (r.status_code != 200):
    print(f'GET request returned a status {r.status_code}')
    exit()

r_to_json = r.json()

# Save tickers trading at >$5 with a dollar volume greater than $20M.
for ticker in r_to_json['results']:
    if ticker['v'] * ticker['c'] > 20000000 and ticker['c'] > 5:
        db[today].insert_one(
            {
            'ticker': ticker['T'],
            'open': ticker['o'],
            'close': ticker['c'],
            'high': ticker['h'],
            'low': ticker['l']
            }
        )
