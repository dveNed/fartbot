# Trading Bot Context Schema Documentation

This document describes the structure and types of the `latest.json` file, which serves as the main input to the AI interpreter logic.

## File Overview
The `latest.json` file is produced by the trading bot every N minutes and contains a complete snapshot of the bot's current state, including market data, positions, and account information.

## Schema Structure

### Top-Level Fields

1. `timestamp` (string)
   - ISO 8601 timestamp when the snapshot was taken
   - Format: "YYYY-MM-DDTHH:MM:SSZ"

2. `prices` (object)
   - Current market prices for all tracked assets
   - Keys: Asset symbols (e.g., "FARTCOIN", "BTC", "SOL")
   - Values: float (current price in USD)

3. `price_deltas` (object)
   - Price change percentages over different timeframes
   - Keys: "{ASSET}_{TIMEFRAME}" (e.g., "FARTCOIN_1m", "BTC_5m")
   - Values: float (percentage change)
   - Timeframes: 1m, 5m, 15m, 1h, etc.

4. `volume_estimates` (object)
   - Estimated 24h trading volume in USD
   - Keys: Asset symbols
   - Values: float (24h volume in USD)

5. `strategy_signals` (object)
   - Current strategy signals for each asset
   - Keys: Asset symbols
   - Values: string ("buy", "sell", "hold")

6. `open_positions` (array)
   - Currently open positions
   - Each position contains:
     - `symbol` (string): Asset symbol
     - `side` (string): "long" or "short"
     - `entry_price` (float): Entry price in USD
     - `size_usd` (float): Position size in USD
     - `unrealized_pnl` (float): Current unrealized P&L in USD
     - `entry_reason` (string): Reason for entry

7. `recent_trades` (array)
   - Last 3-5 completed trades
   - Each trade contains:
     - `symbol` (string): Asset symbol
     - `side` (string): "buy" or "sell"
     - `entry_price` (float): Entry price in USD
     - `exit_price` (float): Exit price in USD
     - `pnl` (float): Realized P&L in USD
     - `entry_reason` (string): Reason for entry
     - `exit_reason` (string): Reason for exit
     - `duration_seconds` (integer): Trade duration in seconds

8. `account` (object)
   - Current account state
   - Fields:
     - `balance` (float): Current balance in USD
     - `pnl_today` (float): Today's P&L in USD
     - `pnl_hour` (float): Last hour's P&L in USD
     - `trades_today` (integer): Number of trades today
     - `trades_this_hour` (integer): Number of trades this hour

9. `meta` (object)
   - Bot metadata
   - Fields:
     - `bot_mode` (string): "paper" or "live"
     - `version` (string): Bot version

## Usage Notes

1. The AI interpreter should:
   - Read and understand the current state
   - Evaluate price trends and risk context
   - Assess current positions
   - Validate strategy signals
   - Provide recommendations in `advice/latest.json`

2. All monetary values are in USD
3. All timestamps are in UTC
4. Price deltas are percentage changes (e.g., -0.23 means -0.23%)
5. The file should be treated as read-only by the AI interpreter 