"""
Discord Trading Bot - Main bot file
Monitors Discord channel for trading signals and executes trades
"""
import asyncio
import logging
import discord
from discord.ext import commands
from signal_parser import SignalParser
from exchange_connector import ExchangeConnector
from trade_executor import TradeExecutor
from config import (
    DISCORD_TOKEN,
    DISCORD_CHANNEL_ID,
    EXCHANGE_NAME,
    EXCHANGE_API_KEY,
    EXCHANGE_API_SECRET,
    USE_TESTNET
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Discord intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Initialize bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize components
signal_parser = SignalParser()
exchange_connector = None
trade_executor = None


@bot.event
async def on_ready():
    """Called when bot is ready"""
    global exchange_connector, trade_executor
    
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guild(s)')
    
    # Initialize exchange connector
    try:
        exchange_connector = ExchangeConnector(
            exchange_name=EXCHANGE_NAME,
            api_key=EXCHANGE_API_KEY,
            api_secret=EXCHANGE_API_SECRET,
            testnet=USE_TESTNET
        )
        trade_executor = TradeExecutor(exchange_connector)
        logger.info("Exchange connector initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize exchange connector: {e}")
        logger.error("Bot will continue but trades cannot be executed")
    
    # Set bot status
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="for trading signals"
        )
    )


@bot.event
async def on_message(message):
    """Handle incoming messages"""
    # Ignore messages from bot itself
    if message.author == bot.user:
        return
    
    # Only process messages from the configured channel
    if message.channel.id != DISCORD_CHANNEL_ID:
        return
    
    # Check if message looks like a trading signal
    if not signal_parser.is_signal_message(message.content):
        return
    
    logger.info(f"Potential signal detected in channel {message.channel.name}")
    logger.info(f"Message content: {message.content[:200]}...")
    
    # Parse the signal
    signal = signal_parser.parse_message(message.content)
    
    if signal:
        logger.info(f"Parsed signal: {signal}")
        
        # Send confirmation to Discord
        embed = discord.Embed(
            title=f"📊 Trading Signal Detected: ${signal.symbol}",
            description="Signal parsed successfully!",
            color=discord.Color.green()
        )
        embed.add_field(name="First Buy Range", value=f"{signal.first_buy_range[0]} - {signal.first_buy_range[1]}", inline=True)
        embed.add_field(name="Second Buy", value=str(signal.second_buy), inline=True)
        embed.add_field(name="CMP", value=str(signal.cmp), inline=True)
        embed.add_field(name="Stop Loss", value=str(signal.stop_loss), inline=True)
        embed.add_field(name="Targets", value=", ".join([f"{t}%" for t in signal.targets]), inline=False)
        
        await message.channel.send(embed=embed)
        
        # Execute the trade if exchange is connected
        if trade_executor:
            logger.info("Executing trade...")
            success = await trade_executor.execute_signal(signal)
            
            if success:
                await message.channel.send(f"✅ Trade execution initiated for ${signal.symbol}")
            else:
                await message.channel.send(f"❌ Failed to execute trade for ${signal.symbol}. Check logs for details.")
        else:
            logger.warning("Trade executor not initialized, cannot execute trade")
            await message.channel.send("⚠️ Exchange not connected. Trade not executed.")
    else:
        logger.warning("Failed to parse signal from message")
        await message.channel.send("❌ Could not parse trading signal. Please check the format.")


@bot.command(name='status')
async def status_command(ctx):
    """Check bot status and active trades"""
    if ctx.channel.id != DISCORD_CHANNEL_ID:
        return
    
    embed = discord.Embed(
        title="🤖 Bot Status",
        color=discord.Color.blue()
    )
    
    # Exchange status
    if exchange_connector:
        try:
            balance = await exchange_connector.get_balance()
            embed.add_field(
                name="Exchange", 
                value=f"✅ Connected ({EXCHANGE_NAME})", 
                inline=False
            )
            embed.add_field(
                name="Balance", 
                value=f"{balance:.2f} USDT", 
                inline=True
            )
        except Exception as e:
            embed.add_field(
                name="Exchange", 
                value=f"❌ Error: {str(e)}", 
                inline=False
            )
    else:
        embed.add_field(
            name="Exchange", 
            value="❌ Not connected", 
            inline=False
        )
    
    # Active trades
    if trade_executor:
        active_trades = trade_executor.get_active_trades()
        if active_trades:
            trades_info = []
            for symbol, trade_info in active_trades.items():
                trades_info.append(
                    f"**${symbol}**: {trade_info['total_amount']:.4f} @ {trade_info['avg_entry_price']:.4f}"
                )
            embed.add_field(
                name="Active Trades",
                value="\n".join(trades_info) if trades_info else "None",
                inline=False
            )
        else:
            embed.add_field(
                name="Active Trades",
                value="None",
                inline=False
            )
    
    await ctx.send(embed=embed)


@bot.command(name='trades')
async def trades_command(ctx):
    """List all active trades"""
    if ctx.channel.id != DISCORD_CHANNEL_ID:
        return
    
    if not trade_executor:
        await ctx.send("❌ Trade executor not initialized")
        return
    
    active_trades = trade_executor.get_active_trades()
    
    if not active_trades:
        await ctx.send("📭 No active trades")
        return
    
    embed = discord.Embed(
        title="📈 Active Trades",
        color=discord.Color.gold()
    )
    
    for symbol, trade_info in active_trades.items():
        signal = trade_info['signal']
        trade_details = (
            f"**Amount**: {trade_info['total_amount']:.4f}\n"
            f"**Avg Entry**: {trade_info['avg_entry_price']:.4f}\n"
            f"**Stop Loss**: {signal.stop_loss}\n"
            f"**Targets**: {', '.join([f'{t}%' for t in signal.targets])}"
        )
        embed.add_field(
            name=f"${symbol}",
            value=trade_details,
            inline=False
        )
    
    await ctx.send(embed=embed)


def main():
    """Main function to run the bot"""
    if not DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not set in environment variables or .env file")
        return
    
    if DISCORD_CHANNEL_ID == 0:
        logger.error("DISCORD_CHANNEL_ID not set in environment variables or .env file")
        return
    
    if not EXCHANGE_API_KEY or not EXCHANGE_API_SECRET:
        logger.warning("Exchange API credentials not set. Bot will run but cannot execute trades.")
    
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Error running bot: {e}")


if __name__ == '__main__':
    main()

