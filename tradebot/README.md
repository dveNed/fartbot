# Fartbot - AI-Powered Paper Trading Bot

A Python-based paper trading bot for Fartcoin using the Hyperliquid exchange.

## Features

- Real-time market data fetching
- Momentum breakout strategy with moving average crossover
- Paper trading simulation
- Comprehensive logging system
- Configurable trading parameters

## Setup

1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Clone the repository and install dependencies:
   ```bash
   git clone <your-repo-url>
   cd fartbot
   poetry install
   ```

3. Create a `.env` file with your configuration:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Run the bot:
   ```bash
   poetry run python main.py
   ```

## Project Structure

```
/fartbot/
├── data/          # Market data storage
├── logs/          # Trading logs
├── .env           # Environment variables
├── config.py      # Configuration settings
├── main.py        # Main bot loop
├── strategy.py    # Trading strategy
├── trade_simulator.py  # Paper trading simulation
├── market_data.py # Market data fetching
└── logger.py      # Logging system
```

## License

MIT 