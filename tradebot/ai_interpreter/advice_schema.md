# AI Interpreter Advice Schema

## Overview
This document describes the schema for the AI Interpreter's output advice file (`advice/latest.json`). The advice file contains structured guidance for the trading bot, including potential overrides to trading signals and risk assessments.

## Schema Definition

```json
{
  "timestamp": "string",           // ISO-8601 formatted timestamp
  "advice": [
    {
      "symbol": "string",          // Trading symbol (e.g., "FARTCOIN", "BTC", "SOL")
      "action": "string",          // One of: "override_signal", "reinforce_signal", "abort_trade", "adjust_risk"
      "new_signal": "string",      // Required for override_signal action, one of: "buy", "sell", "hold"
      "confidence": "number",      // Float between 0.0 and 1.0
      "reason": "string"          // Brief explanation of the advice
    }
  ],
  "overall_risk_level": "string",  // Optional: "low", "medium", "high"
  "notes": "string"               // Optional: Free-form global comments
}
```

## Field Descriptions

### Root Level
- `timestamp`: ISO-8601 formatted timestamp indicating when the advice was generated
- `advice`: Array of advice objects, one per symbol
- `overall_risk_level`: Optional assessment of current market risk
- `notes`: Optional free-form comments about the current market conditions

### Advice Object
- `symbol`: The trading symbol this advice applies to
- `action`: The type of advice being given:
  - `override_signal`: Replace the current trading signal
  - `reinforce_signal`: Confirm the current trading signal
  - `abort_trade`: Cancel any pending trades
  - `adjust_risk`: Modify position sizing or risk parameters
- `new_signal`: Required when action is "override_signal", specifies the new trading direction
- `confidence`: Numerical value between 0.0 and 1.0 indicating the strength of the advice
- `reason`: Brief explanation of why this advice is being given

## Example

```json
{
  "timestamp": "2024-05-02T16:30:00Z",
  "advice": [
    {
      "symbol": "FARTCOIN",
      "action": "override_signal",
      "new_signal": "sell",
      "confidence": 0.87,
      "reason": "Failed breakout pattern detected with 1m price delta < -0.3%"
    }
  ],
  "overall_risk_level": "medium",
  "notes": "BTC showing weakness, monitoring for potential market-wide correction"
}
```

## Validation Rules
1. All timestamps must be valid ISO-8601 strings
2. Confidence values must be between 0.0 and 1.0
3. When action is "override_signal", new_signal must be present
4. Symbols must match the supported trading pairs
5. Action must be one of the defined enum values 