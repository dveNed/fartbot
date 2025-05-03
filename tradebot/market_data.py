from typing import Dict, Optional
import time
from hyperliquid.info import Info
from hyperliquid.utils import constants
from config import config
from logger import logger

class MarketData:
    def __init__(self):
        self.client = Info(
            base_url=config.HYPERLIQUID_API_URL,
            skip_ws=True
        )
        self.prices: Dict[str, float] = {}
        
    def get_price(self, symbol: str) -> Optional[float]:
        """Get the current price for a given symbol"""
        try:
            # Fetch all mid prices from Hyperliquid
            all_mids = self.client.all_mids()
            
            if symbol in all_mids:
                price = float(all_mids[symbol])
                self.prices[symbol] = price
                return price
                
            logger.log_warning(f"No price data available for {symbol}")
            return None
            
        except Exception as e:
            logger.log_error(f"Error fetching price for {symbol}: {e}")
            return None
            
    def update_prices(self) -> Dict[str, float]:
        """Update prices for all trading pairs"""
        try:
            # Fetch all mid prices at once
            all_mids = self.client.all_mids()
            
            # Update prices for configured trading pairs
            for symbol in config.TRADING_PAIRS:
                if symbol in all_mids:
                    self.prices[symbol] = float(all_mids[symbol])
                else:
                    logger.log_warning(f"No price data available for {symbol}")
                    
            return self.prices
            
        except Exception as e:
            logger.log_error(f"Error updating prices: {e}")
            return self.prices
        
    def get_price_history(self, symbol: str, interval: str = '1m', limit: int = 100) -> list:
        """Get historical price data for a symbol"""
        try:
            return self.client.get_candles(symbol, interval, limit)
        except Exception as e:
            logger.log_error(f"Error fetching price history for {symbol}: {e}")
            return []

# Create global market data instance
market_data = MarketData() 