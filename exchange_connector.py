"""
Exchange Connector for executing trades
Supports multiple exchanges via CCXT library
"""
import ccxt
import asyncio
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ExchangeConnector:
    """Handles exchange connections and trade execution"""
    
    def __init__(self, exchange_name: str, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize exchange connector.
        
        Args:
            exchange_name: Name of the exchange (e.g., 'binance', 'binanceus')
            api_key: Exchange API key
            api_secret: Exchange API secret
            testnet: Whether to use testnet
        """
        self.exchange_name = exchange_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.exchange = None
        self._initialize_exchange()
    
    def _initialize_exchange(self):
        """Initialize the CCXT exchange instance"""
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            
            exchange_params = {
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',  # Use spot trading
                }
            }
            
            # Add testnet configuration for Binance
            if self.testnet and self.exchange_name == 'binance':
                exchange_params['options']['defaultType'] = 'future'
                exchange_params['urls'] = {
                    'api': {
                        'public': 'https://testnet.binance.vision/api',
                        'private': 'https://testnet.binance.vision/api',
                    }
                }
            
            self.exchange = exchange_class(exchange_params)
            logger.info(f"Initialized {self.exchange_name} exchange")
            
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            raise
    
    async def get_balance(self, asset: str = 'USDT') -> float:
        """
        Get balance for a specific asset.
        
        Args:
            asset: Asset symbol (e.g., 'USDT')
            
        Returns:
            Available balance
        """
        try:
            balance = await asyncio.to_thread(self.exchange.fetch_balance)
            if asset in balance:
                return float(balance[asset]['free'])
            return 0.0
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return 0.0
    
    async def get_ticker_price(self, symbol: str) -> Optional[float]:
        """
        Get current ticker price for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'LSK/USDT')
            
        Returns:
            Current price or None if error
        """
        try:
            ticker = await asyncio.to_thread(self.exchange.fetch_ticker, symbol)
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            return None
    
    async def place_limit_order(
        self, 
        symbol: str, 
        side: str, 
        amount: float, 
        price: float
    ) -> Optional[Dict]:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair (e.g., 'LSK/USDT')
            side: 'buy' or 'sell'
            amount: Amount to buy/sell
            price: Limit price
            
        Returns:
            Order information or None if error
        """
        try:
            order = await asyncio.to_thread(
                self.exchange.create_limit_order,
                symbol,
                side,
                amount,
                price
            )
            logger.info(f"Placed {side} limit order: {order['id']} for {amount} {symbol} at {price}")
            return order
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            return None
    
    async def place_market_order(
        self, 
        symbol: str, 
        side: str, 
        amount: float
    ) -> Optional[Dict]:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair (e.g., 'LSK/USDT')
            side: 'buy' or 'sell'
            amount: Amount to buy/sell
            
        Returns:
            Order information or None if error
        """
        try:
            order = await asyncio.to_thread(
                self.exchange.create_market_order,
                symbol,
                side,
                amount
            )
            logger.info(f"Placed {side} market order: {order['id']} for {amount} {symbol}")
            return order
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            return None
    
    async def place_stop_loss_order(
        self, 
        symbol: str, 
        amount: float, 
        stop_price: float
    ) -> Optional[Dict]:
        """
        Place a stop loss order.
        
        Args:
            symbol: Trading pair (e.g., 'LSK/USDT')
            amount: Amount to sell
            stop_price: Stop loss price
            
        Returns:
            Order information or None if error
        """
        try:
            # For Binance, use stop limit order
            if self.exchange_name == 'binance':
                # Stop loss is typically a stop-market order
                order = await asyncio.to_thread(
                    self.exchange.create_order,
                    symbol,
                    'STOP_MARKET',
                    'sell',
                    amount,
                    None,
                    None,
                    {'stopPrice': stop_price}
                )
            else:
                # For other exchanges, try stop limit
                order = await asyncio.to_thread(
                    self.exchange.create_order,
                    symbol,
                    'stop',
                    'sell',
                    amount,
                    stop_price,
                    {'stopPrice': stop_price}
                )
            
            logger.info(f"Placed stop loss order: {order['id']} for {amount} {symbol} at {stop_price}")
            return order
        except Exception as e:
            logger.error(f"Error placing stop loss order: {e}")
            # Fallback to limit order if stop loss not supported
            logger.warning("Falling back to limit order for stop loss")
            return await self.place_limit_order(symbol, 'sell', amount, stop_price)
    
    async def place_take_profit_order(
        self, 
        symbol: str, 
        amount: float, 
        target_price: float
    ) -> Optional[Dict]:
        """
        Place a take profit order.
        
        Args:
            symbol: Trading pair (e.g., 'LSK/USDT')
            amount: Amount to sell
            target_price: Take profit price
            
        Returns:
            Order information or None if error
        """
        return await self.place_limit_order(symbol, 'sell', amount, target_price)
    
    def get_symbol(self, base_asset: str, quote_asset: str = 'USDT') -> str:
        """
        Get the trading pair symbol in exchange format.
        
        Args:
            base_asset: Base asset (e.g., 'LSK')
            quote_asset: Quote asset (e.g., 'USDT')
            
        Returns:
            Trading pair symbol (e.g., 'LSK/USDT')
        """
        return f"{base_asset}/{quote_asset}"
    
    async def get_min_order_size(self, symbol: str) -> float:
        """
        Get minimum order size for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Minimum order size
        """
        try:
            markets = await asyncio.to_thread(self.exchange.load_markets)
            if symbol in markets:
                market = markets[symbol]
                return float(market['limits']['amount']['min'])
            return 0.001  # Default minimum
        except Exception as e:
            logger.error(f"Error getting min order size: {e}")
            return 0.001

