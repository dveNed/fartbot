from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from config import config
from logger import logger
from market_data import market_data

@dataclass
class Position:
    symbol: str
    size: float
    entry_price: float
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: Optional[float] = None
    entry_reason: Optional[str] = None
    exit_reason: Optional[str] = None

class TradeSimulator:
    def __init__(self):
        self.balance = config.INITIAL_BALANCE
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Dict] = []
        self.last_stop_loss_time: Optional[datetime] = None
        self.trades_today: int = 0
        self.trades_this_hour: int = 0
        self.last_trade_time: Optional[datetime] = None
        
    def _check_trade_limits(self) -> bool:
        """Check if we're within trade limits"""
        now = datetime.now()
        
        # Reset daily counter if it's a new day
        if self.last_trade_time and self.last_trade_time.date() != now.date():
            self.trades_today = 0
            
        # Reset hourly counter if it's a new hour
        if self.last_trade_time and self.last_trade_time.hour != now.hour:
            self.trades_this_hour = 0
            
        # Check limits
        if self.trades_today >= config.MAX_TRADES_PER_DAY:
            logger.log_warning("Daily trade limit reached")
            return False
            
        if self.trades_this_hour >= config.MAX_TRADES_PER_HOUR:
            logger.log_warning("Hourly trade limit reached")
            return False
            
        return True
        
    def _check_stop_loss_cooldown(self) -> bool:
        """Check if we're in stop loss cooldown period"""
        if not self.last_stop_loss_time:
            return True
            
        cooldown_end = self.last_stop_loss_time + timedelta(minutes=config.STOP_LOSS_COOLDOWN_MINUTES)
        if datetime.now() < cooldown_end:
            logger.log_warning("Still in stop loss cooldown period")
            return False
            
        return True
        
    def calculate_position_size(self, price: float) -> float:
        """Calculate position size based on current balance and position size percentage"""
        position_value = self.balance * config.POSITION_SIZE_PERCENTAGE
        return position_value / price
        
    def open_position(self, symbol: str, signal: str, entry_reason: str) -> bool:
        """Open a new position"""
        try:
            # Check risk management rules
            if not self._check_trade_limits():
                return False
                
            if not self._check_stop_loss_cooldown():
                return False
                
            if len(self.positions) >= config.MAX_OPEN_POSITIONS:
                logger.log_warning("Maximum number of open positions reached")
                return False
                
            if symbol in self.positions:
                logger.log_warning(f"Position already open for {symbol}")
                return False
                
            price = market_data.get_price(symbol)
            if price is None:
                return False
                
            size = self.calculate_position_size(price)
            if size <= 0:
                return False
                
            position = Position(
                symbol=symbol,
                size=size,
                entry_price=price,
                entry_time=datetime.now(),
                entry_reason=entry_reason
            )
            
            self.positions[symbol] = position
            self.trades_today += 1
            self.trades_this_hour += 1
            self.last_trade_time = datetime.now()
            
            logger.log_trade({
                'action': 'open',
                'symbol': symbol,
                'size': size,
                'price': price,
                'balance': self.balance,
                'entry_reason': entry_reason
            })
            
            return True
            
        except Exception as e:
            logger.log_error(f"Error opening position for {symbol}: {e}")
            return False
            
    def close_position(self, symbol: str, exit_reason: str) -> bool:
        """Close an existing position"""
        try:
            if symbol not in self.positions:
                logger.log_warning(f"No position open for {symbol}")
                return False
                
            position = self.positions[symbol]
            price = market_data.get_price(symbol)
            if price is None:
                return False
                
            # Calculate PnL
            pnl = (price - position.entry_price) * position.size
            
            # Update position
            position.exit_price = price
            position.exit_time = datetime.now()
            position.pnl = pnl
            position.exit_reason = exit_reason
            
            # Update balance
            self.balance += pnl
            
            # Check if this was a stop loss
            if exit_reason == 'stop_loss':
                self.last_stop_loss_time = datetime.now()
            
            # Log trade
            logger.log_trade({
                'action': 'close',
                'symbol': symbol,
                'size': position.size,
                'entry_price': position.entry_price,
                'exit_price': price,
                'pnl': pnl,
                'balance': self.balance,
                'entry_reason': position.entry_reason,
                'exit_reason': exit_reason
            })
            
            # Remove position
            del self.positions[symbol]
            
            return True
            
        except Exception as e:
            logger.log_error(f"Error closing position for {symbol}: {e}")
            return False
            
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position for a symbol"""
        return self.positions.get(symbol)
        
    def get_status(self) -> Dict:
        """Get current trading status"""
        return {
            'balance': self.balance,
            'open_positions': len(self.positions),
            'trades_today': self.trades_today,
            'trades_this_hour': self.trades_this_hour,
            'positions': [
                {
                    'symbol': pos.symbol,
                    'size': pos.size,
                    'entry_price': pos.entry_price,
                    'current_price': market_data.get_price(pos.symbol),
                    'unrealized_pnl': (market_data.get_price(pos.symbol) - pos.entry_price) * pos.size if market_data.get_price(pos.symbol) else None
                }
                for pos in self.positions.values()
            ],
            'last_trades': self.trade_history[-3:] if self.trade_history else []
        }

# Create global trade simulator instance
trade_simulator = TradeSimulator() 