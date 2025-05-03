from dataclasses import dataclass, field
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Config:
    # Trading pairs
    TRADING_PAIRS: List[str] = field(default_factory=lambda: ["FARTCOIN", "SOL", "BTC"])
    
    # Data polling interval in seconds
    POLLING_INTERVAL: int = 5
    
    # Strategy parameters
    SHORT_MA_PERIOD: int = 20
    LONG_MA_PERIOD: int = 50
    
    # Paper trading parameters
    INITIAL_BALANCE: float = 1000.0
    MAX_POSITION_SIZE: float = 0.1  # 10% of balance
    
    # Risk management parameters
    MAX_TRADES_PER_HOUR: int = 5
    MAX_TRADES_PER_DAY: int = 20
    MAX_OPEN_POSITIONS: int = 3
    STOP_LOSS_COOLDOWN_MINUTES: int = 30
    POSITION_SIZE_PERCENTAGE: float = 0.01  # 1% of portfolio per trade
    
    # Logging
    LOG_DIR: str = "logs"
    DATA_DIR: str = "data"
    
    # Hyperliquid API settings
    HYPERLIQUID_API_URL: str = os.getenv("HYPERLIQUID_API_URL", "https://api.hyperliquid.xyz")
    HYPERLIQUID_API_KEY: str = os.getenv("HYPERLIQUID_API_KEY", "")
    
    def __post_init__(self):
        # Create directories if they don't exist
        os.makedirs(self.LOG_DIR, exist_ok=True)
        os.makedirs(self.DATA_DIR, exist_ok=True)

# Create global config instance
config = Config() 