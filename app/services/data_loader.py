import yfinance as yf
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.crud.company import get_company_by_symbol, create_company
from app.models.stock import StockData

# ============================
# NSE COMPANIES
# ============================
NSE_COMPANIES = [
    # Large Cap
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS", "ITC.NS",
    # Mid Cap
    "WIPRO.NS", "TITAN.NS", "ASIANPAINT.NS", "MARUTI.NS",
    "SUNPHARMA.NS", "ADANIPORTS.NS", "NTPC.NS", "POWERGRID.NS", "ULTRACEMCO.NS"
]

COMPANY_NAMES = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "ICICIBANK.NS": "ICICI Bank",
    "HINDUNILVR.NS": "Hindustan Unilever",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "ITC.NS": "ITC Limited",
    "WIPRO.NS": "Wipro",
    "TITAN.NS": "Titan Company",
    "ASIANPAINT.NS": "Asian Paints",
    "MARUTI.NS": "Maruti Suzuki",
    "SUNPHARMA.NS": "Sun Pharma",
    "ADANIPORTS.NS": "Adani Ports",
    "NTPC.NS": "NTPC Limited",
    "POWERGRID.NS": "Power Grid Corporation",
    "ULTRACEMCO.NS": "UltraTech Cement"
}

# ============================
# Single Company Data Loader
# ============================
def load_stock_data(db: Session, symbol: str, period: str = "1y"):
    # GET OR CREATE COMPANY
    company = get_company_by_symbol(db, symbol)
    if not company:
        company_name = COMPANY_NAMES.get(symbol, symbol.replace(".NS", ""))
        company = create_company(db, symbol, company_name, "NSE")

    # FETCH DATA
    try:
        df = yf.download(symbol, period=period, progress=False)
        if df.empty:
            return {"symbol": symbol, "status": "No data found"}
    except Exception as e:
        return {"symbol": symbol, "status": f"Error downloading: {str(e)}"}

    # HANDLE MULTIINDEX
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    df = df.reset_index()
    df.rename(columns={df.columns[0]: "Date"}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    # DATA CLEANING
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if any(col not in df.columns for col in required_columns):
        return {"symbol": symbol, "status": "Missing required columns"}

    df.dropna(subset=required_columns, inplace=True)
    if df.empty:
        return {"symbol": symbol, "status": "No valid data after cleaning"}

    # CALCULATED METRICS
    df['daily_return'] = (df['Close'] - df['Open']) / df['Open'].replace(0, np.nan)
    df['ma_7d'] = df['Close'].rolling(window=min(7, len(df)), min_periods=1).mean()
    df['ma_20d'] = df['Close'].rolling(window=min(20, len(df)), min_periods=1).mean()
    df['ma_50d'] = df['Close'].rolling(window=min(50, len(df)), min_periods=1).mean()
    df['week_52_high'] = df['High'].rolling(window=min(252, len(df)), min_periods=1).max()
    df['week_52_low'] = df['Low'].rolling(window=min(252, len(df)), min_periods=1).min()
    df['volatility'] = df['daily_return'].rolling(window=min(7, len(df)), min_periods=1).std()
    df.fillna(0, inplace=True)
    df.replace([float('inf'), float('-inf')], 0, inplace=True)

    # FETCH EXISTING DATES
    existing_dates = {r[0] if not hasattr(r[0], 'date') else r[0].date() 
                    for r in db.query(StockData.date).filter(StockData.company_id == company.id).all()}

    # PREPARE BULK INSERT
    stock_objects = []
    for idx, row in df.iterrows():
        if row['Date'] in existing_dates:
            continue
        stock_objects.append(
            StockData(
                company_id=company.id,
                date=row['Date'],
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=float(row['Volume']),
                daily_return=float(row['daily_return']),
                ma_7d=float(row['ma_7d']),
                ma_20d=float(row['ma_20d']),
                ma_50d=float(row['ma_50d']),
                week_52_high=float(row['week_52_high']),
                week_52_low=float(row['week_52_low']),
                volatility=float(row['volatility'])
            )
        )

    # COMMIT TO DB
    if stock_objects:
        try:
            batch_size = 100
            for i in range(0, len(stock_objects), batch_size):
                db.add_all(stock_objects[i:i+batch_size])
                db.flush()
            db.commit()
            return {"symbol": symbol, "status": f"{len(stock_objects)} new records added"}
        except Exception as e:
            db.rollback()
            return {"symbol": symbol, "status": f"Database error: {str(e)}"}
    else:
        return {"symbol": symbol, "status": "No new data to add"}


# ============================
# Load All NSE Stocks
# ============================
def load_all_stocks(db: Session, symbols: List[str] = None, period: str = "1y"):
    if symbols is None:
        symbols = NSE_COMPANIES

    results = []
    for symbol in symbols:
        result = load_stock_data(db, symbol, period)
        results.append(result)
    return results
