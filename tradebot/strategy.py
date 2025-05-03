from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import json
from pathlib import Path
from config import config
from logger import logger
from market_data import market_data
from ai_interpreter import AdviceEvaluation
from datetime import datetime

class Strategy:
    def __init__(self):
        self.price_history: Dict[str, List[float]] = {
            symbol: [] for symbol in config.TRADING_PAIRS
        }
        self.evaluator = AdviceEvaluation()
        
    def update_price_history(self, symbol: str, price: float):
        """Update price history for a symbol"""
        self.price_history[symbol].append(price)
        # Keep only the last 100 prices for each symbol
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]
            
    def calculate_moving_averages(self, prices: List[float]) -> tuple:
        """Calculate short and long moving averages"""
        if len(prices) < config.LONG_MA_PERIOD:
            return None, None
            
        short_ma = np.mean(prices[-config.SHORT_MA_PERIOD:])
        long_ma = np.mean(prices[-config.LONG_MA_PERIOD:])
        return short_ma, long_ma
        
    def check_btc_trend(self) -> Optional[str]:
        """Check BTC trend to filter trades"""
        btc_prices = self.price_history.get('BTC', [])
        if len(btc_prices) < 2:
            return None
            
        # Simple trend detection
        if btc_prices[-1] > btc_prices[-2]:
            return 'up'
        else:
            return 'down'
            
    def get_ai_advice(self, symbol: str) -> Optional[Dict]:
        """Get AI advice for a symbol"""
        try:
            advice_path = Path("advice/latest.json")
            if not advice_path.exists():
                return None
                
            with open(advice_path, 'r') as f:
                advice = json.load(f)
                
            # Find advice for this symbol
            for rec in advice.get('advice', []):
                if rec['symbol'] == symbol:
                    return rec
                    
            return None
            
        except Exception as e:
            logger.log_error(f"Error reading AI advice for {symbol}: {e}")
            return None
            
    def generate_signal(self, symbol: str) -> str:
        """Generate trading signal for a symbol"""
        try:
            # Update price history
            price = market_data.get_price(symbol)
            if price is None:
                return 'hold'
                
            self.update_price_history(symbol, price)
            
            # Check BTC trend
            btc_trend = self.check_btc_trend()
            if btc_trend == 'down':
                return 'hold'  # Don't trade if BTC is in downtrend
                
            # Calculate moving averages
            short_ma, long_ma = self.calculate_moving_averages(self.price_history[symbol])
            if short_ma is None or long_ma is None:
                return 'hold'
                
            # Generate base signal based on moving average crossover
            base_signal = 'hold'
            if short_ma > long_ma:
                base_signal = 'buy'
            elif short_ma < long_ma:
                base_signal = 'sell'
                
            # Check AI advice
            ai_advice = self.get_ai_advice(symbol)
            if ai_advice and ai_advice['confidence'] >= 0.85:
                if ai_advice['action'] == 'override_signal':
                    logger.log_info(f"AI overriding signal for {symbol}: {base_signal} -> {ai_advice['new_signal']}")
                    return ai_advice['new_signal']
                elif ai_advice['action'] == 'abort_trade':
                    logger.log_info(f"AI aborting trade for {symbol}")
                    return 'hold'
                    
            return base_signal
                
        except Exception as e:
            logger.log_error(f"Error generating signal for {symbol}: {e}")
            return 'hold'
            
    def log_signal_outcome(self, symbol: str, original_signal: str, final_signal: str, pnl: Optional[float] = None):
        """Log the outcome of a trading signal"""
        try:
            ai_advice = self.get_ai_advice(symbol)
            if ai_advice:
                self.evaluator.log_advice_outcome(
                    timestamp=datetime.now().isoformat(),
                    symbol=symbol,
                    action=ai_advice['action'],
                    confidence=ai_advice['confidence'],
                    original_signal=original_signal,
                    applied_signal=final_signal,
                    outcome=pnl > 0 if pnl is not None else None,
                    pnl_impact=pnl
                )
        except Exception as e:
            logger.log_error(f"Error logging signal outcome for {symbol}: {e}")

# Create global strategy instance
strategy = Strategy() 