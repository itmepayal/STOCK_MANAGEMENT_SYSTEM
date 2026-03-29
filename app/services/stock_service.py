import yfinance as yf
from functools import lru_cache

@lru_cache(maxsize=50)
def fetch_stock_data(symbol: str):
    try:
        df = yf.download(symbol, period="1y")

        if df.empty:
            return None

        df = df.reset_index()
        return df

    except Exception as e:
        print("Error fetching data:", e)
        return None
    