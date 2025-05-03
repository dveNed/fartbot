from datetime import datetime
import time
from main import TradingBot
from logger import logger

def test_trading_cycles():
    """Run a few trading cycles to test AI integration"""
    logger.log_info("Starting integration test...")
    
    # Create and start the trading bot
    bot = TradingBot()
    
    # Simulate 3 trading cycles
    for i in range(3):
        logger.log_info(f"\n=== Trading Cycle {i+1} ===")
        
        # Update market data and run AI interpreter
        if (datetime.now() - bot.last_ai_run).total_seconds() >= 300:
            logger.log_info("Running AI interpreter...")
            bot.last_ai_run = datetime.now()
        
        # Process trading pairs
        for symbol in ['FARTCOIN', 'BTC', 'SOL']:
            bot.process_symbol(symbol)
        
        # Print status
        bot.print_status()
        
        # Wait between cycles
        time.sleep(5)
    
    logger.log_info("Integration test completed.")

if __name__ == "__main__":
    test_trading_cycles() 