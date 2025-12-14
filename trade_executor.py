"""
Trade Executor - Handles trade execution logic based on signals
"""
import asyncio
import logging
from typing import List, Optional, Dict
from signal_parser import TradingSignal
from exchange_connector import ExchangeConnector
from config import (
    DEFAULT_QUOTE_ASSET, 
    MAX_POSITION_SIZE, 
    POSITION_SIZE_PERCENTAGE,
    ENABLE_STOP_LOSS,
    ENABLE_TAKE_PROFIT
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TradeExecutor:
    """Executes trades based on trading signals"""
    
    def __init__(self, exchange_connector: ExchangeConnector):
        """
        Initialize trade executor.
        
        Args:
            exchange_connector: ExchangeConnector instance
        """
        self.exchange = exchange_connector
        self.active_trades: Dict[str, Dict] = {}  # Track active trades by symbol
    
    async def execute_signal(self, signal: TradingSignal) -> bool:
        """
        Execute a trading signal.
        
        Args:
            signal: TradingSignal object
            
        Returns:
            True if execution started successfully, False otherwise
        """
        try:
            symbol = self.exchange.get_symbol(signal.symbol, DEFAULT_QUOTE_ASSET)
            
            # Check if we already have an active trade for this symbol
            if signal.symbol in self.active_trades:
                logger.warning(f"Active trade already exists for {signal.symbol}, skipping")
                return False
            
            # Get available balance
            balance = await self.exchange.get_balance(DEFAULT_QUOTE_ASSET)
            if balance < 10:  # Minimum balance check
                logger.error(f"Insufficient balance: {balance} {DEFAULT_QUOTE_ASSET}")
                return False
            
            # Calculate position size
            position_size = min(
                balance * (POSITION_SIZE_PERCENTAGE / 100),
                MAX_POSITION_SIZE
            )
            
            logger.info(f"Executing signal for {signal.symbol}")
            logger.info(f"Available balance: {balance} {DEFAULT_QUOTE_ASSET}")
            logger.info(f"Position size: {position_size} {DEFAULT_QUOTE_ASSET}")
            
            # Split position between first and second buy
            first_buy_size = position_size * 0.6  # 60% for first buy
            second_buy_size = position_size * 0.4  # 40% for second buy
            
            # Execute first buy (average price in range)
            first_buy_price = (signal.first_buy_range[0] + signal.first_buy_range[1]) / 2
            first_buy_amount = first_buy_size / first_buy_price
            
            # Check minimum order size
            min_order_size = await self.exchange.get_min_order_size(symbol)
            if first_buy_amount < min_order_size:
                logger.warning(f"First buy amount {first_buy_amount} below minimum {min_order_size}")
                first_buy_amount = min_order_size
                first_buy_size = first_buy_amount * first_buy_price
            
            # Place first buy order
            logger.info(f"Placing first buy order: {first_buy_amount} {signal.symbol} at {first_buy_price}")
            first_order = await self.exchange.place_limit_order(
                symbol, 
                'buy', 
                first_buy_amount, 
                first_buy_price
            )
            
            if not first_order:
                logger.error("Failed to place first buy order")
                return False
            
            # Store trade information
            total_amount = first_buy_amount
            total_cost = first_buy_size
            
            # Set up second buy order (limit order at second buy price)
            second_buy_amount = second_buy_size / signal.second_buy
            
            if second_buy_amount >= min_order_size:
                logger.info(f"Placing second buy order: {second_buy_amount} {signal.symbol} at {signal.second_buy}")
                second_order = await self.exchange.place_limit_order(
                    symbol,
                    'buy',
                    second_buy_amount,
                    signal.second_buy
                )
                
                if second_order:
                    total_amount += second_buy_amount
                    total_cost += second_buy_size
            
            # Calculate average entry price
            avg_entry_price = total_cost / total_amount if total_amount > 0 else first_buy_price
            
            # Set up stop loss
            stop_loss_order = None
            if ENABLE_STOP_LOSS:
                logger.info(f"Setting up stop loss at {signal.stop_loss}")
                stop_loss_order = await self.exchange.place_stop_loss_order(
                    symbol,
                    total_amount,
                    signal.stop_loss
                )
            
            # Set up take profit targets
            take_profit_orders = []
            if ENABLE_TAKE_PROFIT and signal.targets:
                # Distribute amount across targets
                amount_per_target = total_amount / len(signal.targets)
                
                for target_percent in signal.targets:
                    target_price = avg_entry_price * (1 + target_percent / 100)
                    logger.info(f"Setting up take profit at {target_price} ({target_percent}%)")
                    
                    tp_order = await self.exchange.place_take_profit_order(
                        symbol,
                        amount_per_target,
                        target_price
                    )
                    
                    if tp_order:
                        take_profit_orders.append(tp_order)
            
            # Store active trade
            self.active_trades[signal.symbol] = {
                'symbol': symbol,
                'base_symbol': signal.symbol,
                'first_order': first_order,
                'second_order': second_order if second_buy_amount >= min_order_size else None,
                'stop_loss_order': stop_loss_order,
                'take_profit_orders': take_profit_orders,
                'total_amount': total_amount,
                'avg_entry_price': avg_entry_price,
                'signal': signal
            }
            
            logger.info(f"Trade execution initiated for {signal.symbol}")
            logger.info(f"Average entry price: {avg_entry_price}")
            logger.info(f"Total amount: {total_amount}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing signal: {e}")
            return False
    
    async def check_trade_status(self, symbol: str) -> Optional[Dict]:
        """
        Check the status of an active trade.
        
        Args:
            symbol: Base symbol (e.g., 'LSK')
            
        Returns:
            Trade status information or None
        """
        if symbol not in self.active_trades:
            return None
        
        return self.active_trades[symbol]
    
    def get_active_trades(self) -> Dict[str, Dict]:
        """Get all active trades"""
        return self.active_trades.copy()
    
    def remove_trade(self, symbol: str):
        """Remove a trade from active trades"""
        if symbol in self.active_trades:
            del self.active_trades[symbol]
            logger.info(f"Removed trade for {symbol}")

