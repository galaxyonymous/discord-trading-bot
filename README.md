# Discord Trading Bot

A Python bot that monitors Discord channels for trading signals and automatically executes trades on cryptocurrency exchanges.

## Features

- 🔍 **Automatic Signal Detection**: Monitors Discord channels for trading signals
- 📊 **Signal Parsing**: Extracts trading information from messages (entry prices, targets, stop loss)
- 💱 **Multi-Exchange Support**: Works with Binance and other exchanges via CCXT
- 🎯 **Automated Trading**: Executes buy orders, sets stop loss, and take profit targets
- 📈 **Trade Management**: Tracks active trades and provides status updates

## Signal Format

The bot recognizes signals in the following format:

```
Buying $LSK

First buying: 0.208– 0.210
Second buying: 0.197
CMP: 0.208

Targets
4%
8%
12%
20%
30%

SL: 0.189
```

## Setup

### 1. Prerequisites

- Python 3.8 or higher
- Discord Bot Token
- Exchange API credentials (Binance, etc.)

### 2. Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" section and create a bot
4. Copy the bot token
5. Enable the following intents:
   - MESSAGE CONTENT INTENT
   - SERVER MEMBERS INTENT (if needed)
6. Invite the bot to your server with permissions:
   - Read Messages
   - Send Messages
   - Read Message History

### 4. Get Channel ID

1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode)
2. Right-click on the channel you want to monitor
3. Click "Copy ID"
4. Use this ID in your configuration

### 5. Exchange API Setup

#### For Binance:

1. Log in to Binance
2. Go to API Management
3. Create a new API key
4. **Important**: Enable only "Enable Spot & Margin Trading" (disable withdrawals for security)
5. Copy API Key and Secret Key

#### For Testnet (Recommended for testing):

1. Use Binance Testnet: https://testnet.binance.vision/
2. Create testnet API credentials
3. Set `USE_TESTNET=true` in your `.env` file

### 6. Configuration

1. Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

2. Edit `.env` and fill in your credentials:
```
DISCORD_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_channel_id
EXCHANGE_NAME=binance
EXCHANGE_API_KEY=your_api_key
EXCHANGE_API_SECRET=your_api_secret
USE_TESTNET=false
```

### 7. Configuration Options

- `DISCORD_TOKEN`: Your Discord bot token
- `DISCORD_CHANNEL_ID`: The ID of the channel to monitor
- `EXCHANGE_NAME`: Exchange name (binance, binanceus, etc.)
- `EXCHANGE_API_KEY`: Your exchange API key
- `EXCHANGE_API_SECRET`: Your exchange API secret
- `USE_TESTNET`: Set to `true` to use testnet (recommended for testing)
- `DEFAULT_QUOTE_ASSET`: Quote asset for trading (default: USDT)
- `MAX_POSITION_SIZE`: Maximum position size in quote asset
- `POSITION_SIZE_PERCENTAGE`: Percentage of balance to use per trade
- `ENABLE_STOP_LOSS`: Enable/disable stop loss orders
- `ENABLE_TAKE_PROFIT`: Enable/disable take profit orders

## Usage

### Running the Bot

```bash
python bot.py
```

The bot will:
1. Connect to Discord
2. Connect to the exchange
3. Monitor the specified channel for trading signals
4. Automatically execute trades when signals are detected

### Bot Commands

- `!status` - Check bot status and active trades
- `!trades` - List all active trades with details

## How It Works

1. **Signal Detection**: The bot monitors messages in the configured Discord channel
2. **Signal Parsing**: When a message matches the signal format, it extracts:
   - Symbol (e.g., LSK)
   - Entry prices (first buy range, second buy)
   - Current market price (CMP)
   - Take profit targets (percentages)
   - Stop loss price
3. **Trade Execution**:
   - Calculates position size based on available balance
   - Places limit orders for first and second buy
   - Sets stop loss order
   - Sets take profit orders for each target
4. **Trade Management**: Tracks active trades and provides status updates

## Risk Management

⚠️ **IMPORTANT**: This bot executes real trades with real money. Use at your own risk!

- Always test on testnet first
- Start with small position sizes
- Monitor your trades regularly
- Set appropriate stop losses
- Never share your API keys or Discord token

## Security Best Practices

1. **API Keys**: 
   - Never commit `.env` file to version control
   - Use API keys with limited permissions (disable withdrawals)
   - Consider using IP whitelisting on exchange

2. **Discord Token**:
   - Keep your bot token secret
   - Regenerate if compromised

3. **Testnet First**:
   - Always test on testnet before using real funds
   - Verify signal parsing works correctly
   - Test with small amounts first

## Troubleshooting

### Bot not connecting to Discord
- Check if DISCORD_TOKEN is correct
- Verify bot has necessary permissions
- Check if intents are enabled in Discord Developer Portal

### Bot not detecting signals
- Verify DISCORD_CHANNEL_ID is correct
- Check if message format matches expected format
- Enable message content intent

### Exchange connection errors
- Verify API keys are correct
- Check if API has trading permissions
- For Binance, ensure IP whitelist allows your IP (if enabled)

### Trade execution failures
- Check account balance
- Verify symbol exists on exchange (e.g., LSK/USDT)
- Check minimum order size requirements
- Review exchange API rate limits

## Supported Exchanges

The bot uses CCXT library, which supports 100+ exchanges. Currently tested with:
- Binance
- Binance US

To use other exchanges, change `EXCHANGE_NAME` in your `.env` file.

## License

This project is provided as-is for educational purposes. Use at your own risk.

## Disclaimer

This bot is for educational purposes only. Trading cryptocurrencies involves substantial risk. Always do your own research and never invest more than you can afford to lose. The authors are not responsible for any financial losses.

