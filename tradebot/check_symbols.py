from hyperliquid.info import Info
from config import config

def check_symbols():
    client = Info(
        base_url=config.HYPERLIQUID_API_URL,
        skip_ws=True
    )
    
    all_mids = client.all_mids()
    print("Available symbols:", list(all_mids.keys()))

if __name__ == "__main__":
    check_symbols() 