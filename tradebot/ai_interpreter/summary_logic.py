from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MarketSummary:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.direction: Optional[str] = None  # 'up', 'down', 'flat'
        self.high_volatility: bool = False
        self.volume_spike: bool = False
        self.price_delta: float = 0.0
        self.volume_delta: Optional[float] = None

def load_context() -> Dict:
    """Load the latest context from context/latest.json"""
    context_path = Path("context/latest.json")
    logger.debug(f"Loading context from {context_path.absolute()}")
    
    if not context_path.exists():
        raise FileNotFoundError("Context file not found")
    
    try:
        with open(context_path, 'r') as f:
            content = f.read()
            logger.debug(f"Raw content: {content[:100]}...")  # First 100 chars
            return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        raise

def compress_context(context: Dict) -> Dict[str, MarketSummary]:
    """Compress raw context into a summary of market conditions"""
    summaries = {}
    logger.debug(f"Compressing context with keys: {list(context.keys())}")
    
    # Process each symbol's data
    for symbol in context.get('prices', {}).keys():
        summary = MarketSummary(symbol)
        
        # Get price deltas
        price_deltas = context.get('price_deltas', {})
        delta_key = f"{symbol}_5m"
        if delta_key in price_deltas:
            delta = price_deltas[delta_key]
            summary.price_delta = delta
            
            # Determine direction
            if abs(delta) < 0.2:
                summary.direction = 'flat'
            else:
                summary.direction = 'up' if delta > 0 else 'down'
            
            # Check for high volatility
            summary.high_volatility = abs(delta) > 1.0
        
        # Check for volume spikes if volume data is available
        volumes = context.get('volumes', {})
        if volumes and symbol in volumes:
            current_volume = volumes[symbol]
            avg_volume = context.get('volume_averages', {}).get(symbol, 0)
            if avg_volume > 0:
                volume_ratio = current_volume / avg_volume
                summary.volume_spike = volume_ratio > 2.0
                summary.volume_delta = volume_ratio - 1.0
        
        summaries[symbol] = summary
        logger.debug(f"Created summary for {symbol}: direction={summary.direction}, volatility={summary.high_volatility}")
    
    return summaries

def assess_risk_level(context: Dict, summaries: Dict[str, MarketSummary]) -> str:
    """Assess overall market risk level"""
    # Check BTC performance
    btc_summary = summaries.get('BTC')
    if btc_summary and btc_summary.price_delta < -1.0:
        logger.debug("High risk: BTC price delta < -1.0%")
        return 'high'
    
    # Check for multiple high volatility symbols
    high_vol_count = sum(1 for s in summaries.values() if s.high_volatility)
    if high_vol_count >= 2:
        logger.debug(f"Medium risk: {high_vol_count} symbols with high volatility")
        return 'medium'
    
    logger.debug("Low risk conditions")
    return 'low'

def get_recent_trade_outcome(context: Dict, symbol: str) -> Optional[bool]:
    """Check if the last trade for a symbol was profitable"""
    recent_trades = context.get('recent_trades', [])
    symbol_trades = [t for t in recent_trades if t.get('symbol') == symbol]
    
    if not symbol_trades:
        return None
    
    last_trade = symbol_trades[-1]
    return last_trade.get('pnl', 0) > 0

def get_trade_count_this_hour(context: Dict) -> int:
    """Count trades in the last hour"""
    recent_trades = context.get('recent_trades', [])
    now = datetime.now()
    hour_ago = now.timestamp() - 3600
    
    return sum(1 for t in recent_trades 
              if datetime.fromisoformat(t['timestamp']).timestamp() > hour_ago) 