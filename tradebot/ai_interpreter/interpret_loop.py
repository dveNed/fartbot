import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from .summary_logic import (
    load_context,
    compress_context,
    assess_risk_level,
    get_recent_trade_outcome,
    get_trade_count_this_hour,
    MarketSummary
)

def generate_advice() -> Dict:
    """Generate trading advice based on current market context"""
    try:
        context = load_context()
        summaries = compress_context(context)
        risk_level = assess_risk_level(context, summaries)
        
        advice = {
            "timestamp": datetime.now().isoformat(),
            "advice": [],
            "overall_risk_level": risk_level,
            "notes": ""
        }
        
        # Process each symbol
        for symbol, summary in summaries.items():
            symbol_advice = analyze_symbol(context, symbol, summary, risk_level, summaries)
            if symbol_advice:
                advice["advice"].append(symbol_advice)
        
        # Add global notes based on market conditions
        if risk_level == "high":
            advice["notes"] = "High risk conditions detected. Exercise caution with new positions."
        elif any(s.volume_spike for s in summaries.values()):
            advice["notes"] = "Volume spikes detected in one or more symbols."
        
        return advice
    
    except Exception as e:
        # Return safe default advice in case of errors
        return {
            "timestamp": datetime.now().isoformat(),
            "advice": [],
            "overall_risk_level": "medium",
            "notes": f"Error generating advice: {str(e)}"
        }

def analyze_symbol(context: Dict, symbol: str, summary: MarketSummary, risk_level: str, summaries: Dict[str, MarketSummary]) -> Dict:
    """Analyze a specific symbol and generate advice"""
    base_confidence = 0.60
    advice = {
        "symbol": symbol,
        "confidence": base_confidence,
        "reason": ""
    }
    
    # Rule 1: Abort longs if BTC is down and risk is medium+
    if symbol != "BTC" and risk_level in ["medium", "high"]:
        btc_summary = summaries.get("BTC")
        if btc_summary and btc_summary.price_delta < -1.0:
            advice.update({
                "action": "abort_trade",
                "reason": "BTC showing weakness with risk level elevated"
            })
            advice["confidence"] += 0.15
            return advice
    
    # Rule 2: Override FARTCOIN on failed breakout
    if symbol == "FARTCOIN":
        price_delta_1m = context.get('price_deltas', {}).get('FARTCOIN_1m', 0)
        last_trade_profit = get_recent_trade_outcome(context, symbol)
        
        if price_delta_1m < -0.3 and last_trade_profit is False:
            advice.update({
                "action": "override_signal",
                "new_signal": "sell",
                "reason": "Failed breakout detected with recent loss"
            })
            advice["confidence"] += 0.20
            return advice
    
    # Rule 3: Reinforce hold in flat market
    if summary.direction == "flat" and not context.get('open_positions', {}).get(symbol):
        advice.update({
            "action": "reinforce_signal",
            "reason": "Market is flat with no open positions"
        })
        advice["confidence"] += 0.10
        return advice
    
    # Adjust confidence based on trade frequency
    trade_count = get_trade_count_this_hour(context)
    max_allowed_trades = context.get('max_trades_per_hour', 10)
    if trade_count >= 0.8 * max_allowed_trades:
        advice["confidence"] -= 0.10
    
    return None  # No specific advice for this symbol

def write_advice(advice: Dict):
    """Write advice to advice/latest.json"""
    advice_dir = Path("advice")
    advice_dir.mkdir(exist_ok=True)
    
    with open(advice_dir / "latest.json", 'w') as f:
        json.dump(advice, f, indent=2)

def run():
    """Main entry point for the interpreter loop"""
    advice = generate_advice()
    write_advice(advice)
    return advice

if __name__ == "__main__":
    run() 