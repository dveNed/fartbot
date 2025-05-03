import time
import signal
import sys
from datetime import datetime
from config import config
from logger import logger
from market_data import market_data
from strategy import strategy
from trade_simulator import trade_simulator
from ai_interpreter import run as run_interpreter

class TradingBot:
    def __init__(self):
        self.running = True
        self.last_status_print = datetime.now()
        self.last_ai_run = datetime.now()
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.handle_interrupt)
        signal.signal(signal.SIGTERM, self.handle_interrupt)
        
    def handle_interrupt(self, signum, frame):
        """Handle interrupt signals"""
        logger.log_info("Shutting down trading bot...")
        self.running = False
        
    def print_status(self):
        """Print current trading status"""
        status = trade_simulator.get_status()
        
        print("\n=== Trading Status ===")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Balance: ${status['balance']:.2f}")
        print(f"Open Positions: {status['open_positions']}")
        print(f"Trades Today: {status['trades_today']}/{config.MAX_TRADES_PER_DAY}")
        print(f"Trades This Hour: {status['trades_this_hour']}/{config.MAX_TRADES_PER_HOUR}")
        
        if status['positions']:
            print("\nOpen Positions:")
            for pos in status['positions']:
                pnl = pos['unrealized_pnl']
                pnl_str = f"${pnl:.2f}" if pnl is not None else "N/A"
                print(f"  {pos['symbol']}: {pos['size']} @ ${pos['entry_price']:.2f} (Current: ${pos['current_price']:.2f}, PnL: {pnl_str})")
                
        if status['last_trades']:
            print("\nLast 3 Trades:")
            for trade in status['last_trades']:
                print(f"  {trade['timestamp']} - {trade['action']} {trade['symbol']} @ ${trade['price']:.2f}")
                if trade['action'] == 'close':
                    print(f"    PnL: ${trade['pnl']:.2f}, Reason: {trade['exit_reason']}")
                else:
                    print(f"    Reason: {trade['entry_reason']}")
                    
        print("\n" + "="*50 + "\n")
        
    def process_symbol(self, symbol: str):
        """Process a single trading symbol"""
        try:
            # Get current price
            price = market_data.get_price(symbol)
            if price is None:
                logger.log_warning(f"Could not get price for {symbol}, skipping this cycle")
                return
                
            logger.log_info(f"Current price for {symbol}: {price}")
                
            # Generate trading signal
            original_signal = strategy.generate_signal(symbol)
            logger.log_info(f"Generated signal for {symbol}: {original_signal}")
            
            # Get current position
            position = trade_simulator.get_position(symbol)
            logger.log_info(f"Current position for {symbol}: {position}")
            
            # Handle trading signals
            if original_signal == 'buy' and not position:
                logger.log_info(f"Opening position for {symbol}")
                trade_simulator.open_position(symbol, original_signal, "Moving average crossover")
                strategy.log_signal_outcome(symbol, original_signal, original_signal)
            elif original_signal == 'sell' and position:
                logger.log_info(f"Closing position for {symbol}")
                pnl = trade_simulator.close_position(symbol, "Moving average crossover")
                strategy.log_signal_outcome(symbol, original_signal, original_signal, pnl)
                
        except Exception as e:
            logger.log_error(f"Error processing {symbol}: {e}")
            
    def run(self):
        """Main trading loop"""
        logger.log_info("Starting trading bot...")
        
        # Test market data connection
        try:
            initial_prices = market_data.update_prices()
            logger.log_info("Initial market data fetch successful")
            logger.log_info(f"Current prices: {initial_prices}")
        except Exception as e:
            logger.log_error(f"Failed to fetch initial market data: {e}")
            logger.log_error("Bot will continue but may not have accurate price data")
        
        while self.running:
            try:
                # Update market data
                prices = market_data.update_prices()
                logger.log_info(f"Updated market prices: {prices}")
                
                # Run AI interpreter every 5 minutes
                if (datetime.now() - self.last_ai_run).total_seconds() >= 300:
                    try:
                        logger.log_info("Running AI interpreter...")
                        run_interpreter()
                        self.last_ai_run = datetime.now()
                    except Exception as e:
                        logger.log_error(f"Error running AI interpreter: {e}")
                
                # Process each trading pair
                for symbol in config.TRADING_PAIRS:
                    self.process_symbol(symbol)
                    
                # Print status every 30 seconds
                if (datetime.now() - self.last_status_print).total_seconds() >= 30:
                    self.print_status()
                    self.last_status_print = datetime.now()
                    
                # Sleep for polling interval
                time.sleep(config.POLLING_INTERVAL)
                
            except Exception as e:
                logger.log_error(f"Error in main loop: {e}")
                time.sleep(config.POLLING_INTERVAL)
                
        logger.log_info("Trading bot stopped")

if __name__ == "__main__":
    bot = TradingBot()
    bot.run() 