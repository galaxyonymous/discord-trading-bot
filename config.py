"""
Configuration file for the trading bot.
Set your credentials in .env file or update these values directly.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', '')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID', 0))

# Exchange Configuration
EXCHANGE_NAME = os.getenv('EXCHANGE_NAME', 'binance')  # binance, binanceus, etc.
EXCHANGE_API_KEY = os.getenv('EXCHANGE_API_KEY', '')
EXCHANGE_API_SECRET = os.getenv('EXCHANGE_API_SECRET', '')

# Trading Configuration
USE_TESTNET = os.getenv('USE_TESTNET', 'false').lower() == 'true'
DEFAULT_QUOTE_ASSET = os.getenv('DEFAULT_QUOTE_ASSET', 'USDT')  # USDT, BUSD, etc.
MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '100'))  # Maximum position size in quote asset
POSITION_SIZE_PERCENTAGE = float(os.getenv('POSITION_SIZE_PERCENTAGE', '10'))  # Percentage of balance to use per trade

# Risk Management
ENABLE_STOP_LOSS = os.getenv('ENABLE_STOP_LOSS', 'true').lower() == 'true'
ENABLE_TAKE_PROFIT = os.getenv('ENABLE_TAKE_PROFIT', 'true').lower() == 'true'

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

