import yfinance as yf
import pandas as pd  # noqa: F401
import numpy as np  # noqa: F401

def v2_load_and_sync_data(period="5y", interval="1d"):
    """
    Loads historical data for Gold, Silver, Platinum, Palladium and BTC.
    """

    tickers =  {
        'Gold': 'GC=F',
        'Silver': 'SI=F',
        'Platinum': 'PL=F',
        'Palladium': 'PA=F',
        'Copper': 'HG=F',    # added copper
        'BTC': 'BTC-USD'
    }
    print(f"--- Downloading data for: {list(tickers.keys())} ---")
    data = yf.download(list(tickers.values()), period=period, interval=interval)['Close']
    inv_tickers = {v: k for k, v in tickers.items()}
    data = data.rename(columns=inv_tickers)
    data = data.ffill().dropna()
    for metal in ['Gold', 'Silver', 'Platinum', 'Palladium', 'Copper']:
        data[f'{metal}_BTC_Corr'] = data[metal].rolling(window=30).corr(data['BTC'])
    for asset in ['Gold', 'Silver', 'Platinum', 'Palladium', 'Copper', 'BTC']:
        data[f'{asset}_Pct_change'] = data[asset].pct_change()
        data[f'{asset}_Lag1'] = data[asset].shift(1)
    return data.dropna()

if __name__ == "__main__":
    df = v2_load_and_sync_data()
    print("\n--- Sample of the loaded and synchronized data ---")
    print(df[['Gold', 'Silver', 'Platinum', 'Palladium', 'Copper', 'BTC', 'Gold_BTC_Corr', 'Silver_BTC_Corr']].tail())
    df.to_csv("v2_market_data.csv")
    print("\nFile 'v2_market_data.csv' saved successfully!") 