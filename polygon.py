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
data_date = str(datetime.today().strftime('%Y-%m-%d'))

# Polygon API endpoint payload.
payload = {
    'unadjusted': 'true',
    'apiKey': os.environ['POLYGON_API_KEY']
}

# API endpoint for all US stock ticker symbols.
url = f'https://api.polygon.io/v2/aggs/grouped/locale/us/market/stocks/{data_date}?'

r = requests.get(url, params=payload)

# Check if Polygon's API returns status 200.
if (r.status_code != 200):
    print(f'GET request returned a status {r.status_code}')
    exit()

r_to_json = r.json()

today = str(datetime.today().strftime('%Y-%m-%d'))

# Save tickers trading at >$5, that closed 5% up, and had at least 500K volume.
for ticker in r_to_json['results']:
    if ticker['o'] > 5 and ticker['c'] > (ticker['o'] * 1.05) and ticker['v'] > 500000:
        db[today].insert_one(
            {
            'ticker': ticker['T'],
            'open': ticker['o'],
            'close': ticker['c'],
            'high': ticker['h'],
            'low': ticker['l']
            }
        )
