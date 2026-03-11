import yfinance as yf
import pandas as pd  # noqa: F401
import numpy as np  # noqa: F401
import pandas_ta as ta
from pathlib import Path

def rebuild():
    """Fetch full history and compute all features, then write snapshot."""
    base_path = Path(__file__).parent
    output = base_path / 'v2_final_market_snapshot.csv'
    # define tickers
    tickers = {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Platinum": "PL=F",
        "Palladium": "PA=F",
        "Copper": "HG=F",
        "BTC": "BTC-USD"
    }
    inv = {v:k for k,v in tickers.items()}

    print("Downloading full history for all tickers...")
    df = yf.download(list(tickers.values()), period="max", interval="1d")["Close"]
    df = df.rename(columns=inv)

    # compute features on the full DataFrame
    for metal in tickers.keys():
        df[f"{metal}_Lag1"] = df[metal].shift(1)
        df[f"{metal}_Lag3"] = df[metal].shift(3)
        df[f"{metal}_MA7"] = df[metal].rolling(window=7).mean()
        df[f"{metal}_Pct_change"] = df[metal].pct_change()
        df[f"{metal}_RSI_14"] = ta.rsi(df[metal], length=14)
        macd_vals = ta.macd(df[metal], fast=12, slow=26, signal=9)
        df[f"{metal}_MACD"] = macd_vals.get("MACD_12_26_9")
        if metal != "BTC":
            df[f"{metal}_BTC_Corr"] = df[metal].rolling(window=14).corr(df["BTC"])

    # reset index to bring Date back as a column and reorder
    final = df.reset_index()
    cols = final.columns.tolist()
    if "Date" in cols:
        cols.insert(0, cols.pop(cols.index("Date")))
        final = final[cols]

    print(f"Saving reconstructed snapshot with {len(final)} rows and {len(final.columns)} columns")
    final.to_csv(output, index=False)


if __name__ == '__main__':
    rebuild()
