import os
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
from pymongo import MongoClient

# Import MongoDB credentials.
mongo_pw = os.environ['MONGO_USER_PASSWORD']
mongo_db = os.environ['MONGO_DB_NAME']

# Import our Alpaca API keys.
APCA_API_KEY_ID = os.environ['APCA_API_KEY_ID']
APCA_API_SECRET_KEY = os.environ['APCA_API_SECRET_KEY']
APCA_API_BASE_URL = os.environ['APCA_API_BASE_URL']

# Establish rest connection with Alpaca's API using our keys.
api = tradeapi.REST(
    APCA_API_KEY_ID,
    APCA_API_SECRET_KEY,
    APCA_API_BASE_URL
)

# Connect to our db.
mongo_uri = f'mongodb+srv://cberg:{mongo_pw}@cluster0.2av1u.mongodb.net/{mongo_db}?retryWrites=true&w=majority'

client = MongoClient(mongo_uri)

db = client.alpha_vantage

# Check if market is open.
clock = api.get_clock()

account = api.get_account()
history = api.get_portfolio_history()

print(history)
