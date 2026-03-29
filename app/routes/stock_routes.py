from fastapi import APIRouter, HTTPException, Query
from functools import lru_cache
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

router = APIRouter()

# List of companies
COMPANIES = ["INFY.NS", "TCS.NS", "RELIANCE.NS"]

# -------------------------
# Utility functions
# -------------------------
@lru_cache(maxsize=50)
def fetch_stock_data(symbol: str) -> pd.DataFrame | None:
    """
    Fetch stock data using yfinance and cache results.
    Returns None if symbol is invalid.
    """
    try:
        df = yf.download(symbol, period="1y")
        if df.empty:
            return None
        df = df.reset_index()
        return df
    except Exception as e:
        print("Error fetching data:", e)
        return None

def add_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds custom metrics to the stock DataFrame.
    """
    df["daily_return"] = (df["Close"] - df["Open"]) / df["Open"]
    df["7d_ma"] = df["Close"].rolling(7).mean()
    df["52_week_high"] = df["Close"].rolling(252).max()
    df["52_week_low"] = df["Close"].rolling(252).min()
    df["volatility"] = df["daily_return"].rolling(7).std()
    return df

def get_summary(df: pd.DataFrame) -> dict:
    """
    Returns 52-week high, low, and average close.
    """
    return {
        "52_week_high": float(df["Close"].max()),
        "52_week_low": float(df["Close"].min()),
        "avg_close": float(df["Close"].mean()),
    }

def get_signal(df: pd.DataFrame) -> str:
    """
    Simple signal: Buy if 7d_ma < Close, Sell if 7d_ma > Close
    """
    if df["7d_ma"].iloc[-1] < df["Close"].iloc[-1]:
        return "BUY"
    else:
        return "SELL"

# -------------------------
# Endpoints
# -------------------------
@router.get("/companies")
def get_companies():
    return COMPANIES

@router.get("/data/{symbol}")
def get_stock_data(symbol: str):
    df = fetch_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail="Invalid symbol")
    df = add_metrics(df)
    return df.tail(30).to_dict(orient="records")

@router.get("/summary/{symbol}")
def summary(symbol: str):
    df = fetch_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail="Invalid symbol")
    df = add_metrics(df)
    return {**get_summary(df), "signal": get_signal(df)}

@router.get("/compare")
def compare(symbol1: str = Query(...), symbol2: str = Query(...)):
    df1 = fetch_stock_data(symbol1)
    df2 = fetch_stock_data(symbol2)
    if df1 is None or df2 is None:
        raise HTTPException(status_code=404, detail="Invalid symbol")
    df1 = add_metrics(df1)
    df2 = add_metrics(df2)
    return {
        symbol1: {
            "return": float(df1["daily_return"].sum()),
            "volatility": float(df1["volatility"].mean())
        },
        symbol2: {
            "return": float(df2["daily_return"].sum()),
            "volatility": float(df2["volatility"].mean())
        }
    }

@router.get("/correlation")
def correlation(symbol1: str = Query(...), symbol2: str = Query(...)):
    df1 = fetch_stock_data(symbol1)
    df2 = fetch_stock_data(symbol2)
    if df1 is None or df2 is None:
        raise HTTPException(status_code=404, detail="Invalid symbol")
    return {"correlation": float(df1["Close"].corr(df2["Close"]))}

@router.get("/top-gainers")
def top_gainers():
    results = []
    for symbol in COMPANIES:
        df = fetch_stock_data(symbol)
        if df is None:
            continue
        df = add_metrics(df)
        returns = df["daily_return"].sum()
        results.append({"symbol": symbol, "returns": float(returns)})
    return sorted(results, key=lambda x: x["returns"], reverse=True)

@router.get("/volatility/{symbol}")
def volatility(symbol: str):
    df = fetch_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail="Invalid symbol")
    df = add_metrics(df)
    return {"symbol": symbol, "volatility": float(df["volatility"].iloc[-1])}

@router.get("/data-range/{symbol}")
def data_range(symbol: str, days: int = 30):
    df = fetch_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail="Invalid symbol")
    df = add_metrics(df)
    return df.tail(days).to_dict(orient="records")

@router.get("/signal/{symbol}")
def signal(symbol: str):
    df = fetch_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail="Invalid symbol")
    df = add_metrics(df)
    return {"symbol": symbol, "signal": get_signal(df)}

@router.get("/predict/{symbol}")
def predict(symbol: str):
    df = fetch_stock_data(symbol)
    if df is None:
        raise HTTPException(status_code=404, detail="Invalid symbol")
    df = df.reset_index()
    df["Days"] = np.arange(len(df))
    X = df[["Days"]]
    y = df["Close"]
    model = LinearRegression()
    model.fit(X, y)
    next_day = np.array([[len(df)]])
    prediction = model.predict(next_day)
    return {"symbol": symbol, "predicted_price": float(prediction[0])}