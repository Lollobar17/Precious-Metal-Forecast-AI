import yfinance as yf
import pandas as pd
import os

def download_data(ticker='GC=F', start='2010-01-01'):
    """
    Downloads historical data for Gold, Copper and correlated market indices.
    GC=F is the ticker for Gold Futures on Yahoo Finance and HG=F for Copper Futures.
    """

    if not os.path.exists('data'):
        os.makedirs('data')

    print("--- Downloading Gold, Copper, USD Index, and S&P500 ---")
    
    data = yf.download(["GC=F", "HG=F", "DX=F", "^GSPC"], start=start)['Close']

    df = pd.DataFrame()
    df['Gold'] = data['GC=F']
    df['Copper'] = data['HG=F']
    df['USD_Index'] = data['DX=F']
    df['S&P500'] = data['^GSPC']
    df['Returns'] = df['Gold'].pct_change()

    df = df.dropna()

    df.to_csv("data/gold_data.csv")
    print(f"Success! Gold is at ${df['Gold'].iloc[-1]:.2f}")
    return df

if __name__ == "__main__":
    download_data()
