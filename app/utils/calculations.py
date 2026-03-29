import pandas as pd

def add_metrics(df: pd.DataFrame):
    if df is None or df.empty:
        return None

    df = df.copy()

    # Clean data
    df = df.fillna(method="ffill")

    # Metrics
    df["Daily Return"] = (df["Close"] - df["Open"]) / df["Open"]
    df["MA7"] = df["Close"].rolling(7).mean()
    df["Volatility"] = df["Daily Return"].rolling(7).std()

    df["MA50"] = df["Close"].rolling(50).mean()
    df["MA200"] = df["Close"].rolling(200).mean()

    return df


def get_summary(df: pd.DataFrame):
    return {
        "52_week_high": float(df["High"].max()),
        "52_week_low": float(df["Low"].min()),
        "avg_close": float(df["Close"].mean()),
        "volatility": float(df["Volatility"].mean())
    }


def get_signal(df: pd.DataFrame):
    latest = df.iloc[-1]

    if latest["MA50"] > latest["MA200"]:
        return "Strong Bullish"
    elif latest["Close"] > latest["MA7"]:
        return "Bullish"
    else:
        return "Bearish"
    