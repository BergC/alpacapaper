import os
import alpaca_trade_api as tradeapi


# Import our API keys.
APCA_API_KEY_ID = os.environ['APCA_API_KEY_ID']
APCA_API_SECRET_KEY = os.environ['APCA_API_SECRET_KEY']
APCA_API_BASE_URL = os.environ['APCA_API_BASE_URL']

# Establish rest connection with Alpaca's API using our keys.
api = tradeapi.REST(
    APCA_API_KEY_ID,
    APCA_API_SECRET_KEY,
    APCA_API_BASE_URL
)

# Check if market is open.
clock = api.get_clock()
print('The market is {}'.format('open.' if clock.is_open else 'closed.'))

# Get our account information.
# account = api.get_account()
# print(account)

