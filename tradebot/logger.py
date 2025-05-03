import logging
import os
from datetime import datetime
import json
import csv
from typing import Dict, Any
from config import config

class Logger:
    def __init__(self):
        self.log_dir = config.LOG_DIR
        self.setup_logging()
        self.setup_trade_logging()
        
    def setup_logging(self):
        """Set up logging configuration"""
        # Create logs directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(self.log_dir, 'trading.log')),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def setup_trade_logging(self):
        """Set up trade logging to CSV"""
        self.trades_csv = os.path.join(self.log_dir, 'trades.csv')
        if not os.path.exists(self.trades_csv):
            with open(self.trades_csv, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp',
                    'action',
                    'symbol',
                    'size',
                    'price',
                    'entry_price',
                    'exit_price',
                    'pnl',
                    'balance',
                    'entry_reason',
                    'exit_reason'
                ])
        
    def log_trade(self, trade_data: Dict[str, Any]):
        """Log a trade to both the log file and CSV"""
        # Log to console and file
        self.logger.info(f"Trade executed: {trade_data}")
        
        # Append to trades CSV
        timestamp = datetime.now().isoformat()
        with open(self.trades_csv, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                trade_data.get('action'),
                trade_data.get('symbol'),
                trade_data.get('size'),
                trade_data.get('price'),
                trade_data.get('entry_price'),
                trade_data.get('exit_price'),
                trade_data.get('pnl'),
                trade_data.get('balance'),
                trade_data.get('entry_reason'),
                trade_data.get('exit_reason')
            ])
            
        # Also append to trades JSON for quick access
        trades_file = os.path.join(self.log_dir, 'trades.json')
        trade_data['timestamp'] = timestamp
        
        try:
            if os.path.exists(trades_file):
                with open(trades_file, 'r') as f:
                    trades = json.load(f)
            else:
                trades = []
                
            trades.append(trade_data)
            
            with open(trades_file, 'w') as f:
                json.dump(trades, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error logging trade to JSON: {e}")
            
    def log_error(self, error_message: str):
        """Log an error message"""
        self.logger.error(error_message)
        
    def log_info(self, info_message: str):
        """Log an info message"""
        self.logger.info(info_message)
        
    def log_warning(self, warning_message: str):
        """Log a warning message"""
        self.logger.warning(warning_message)

# Create global logger instance
logger = Logger() 