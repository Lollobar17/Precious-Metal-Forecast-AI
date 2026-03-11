import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
import os

def update_market_snapshot():
    """
    V4 Live Data Engine:
    Downloads the latest market prices, calculates lags/correlations, and updates the historical snapshot CSV.
    """

    print("\n" + "="*50)
    print("V4 Live Data Engine: Updating Market Snapshot")
    print("="*50)

    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_path, 'v2_final_market_snapshot.csv')
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please run the initial snapshot creation first.")
        return

    # load old snapshot keeping the Date column; parse it explicitly
    df_old = pd.read_csv(csv_path, parse_dates=['Date'])
    # unify any previous inconsistent pct naming and drop duplicates
    df_old.columns = [c.replace('_Pct_Change', '_Pct_change') for c in df_old.columns]
    df_old = df_old.loc[:, ~df_old.columns.duplicated()]
    # determine latest date present
    last_date_in_csv = pd.to_datetime(df_old['Date'].max())
    # ensure Date column is first for readability
    if 'Date' in df_old.columns:
        cols = df_old.columns.tolist()
        cols.insert(0, cols.pop(cols.index('Date')))
        df_old = df_old[cols]
    print(f"Loaded existing snapshot with {len(df_old)} records.")

    tickers = {
        "Gold": "GC=F",
        "Silver": "SI=F",
        "Platinum": "PL=F",
        "Palladium": "PA=F",
        "Copper": "HG=F",
        "BTC": "BTC-USD"
    }

    print("Fetching latest market data...")
    try:
        new_data = yf.download(list(tickers.values()), period="60d", interval="1d")['Close']

    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    inv_tickers = {v: k for k, v in tickers.items()}
    new_data = new_data.rename(columns=inv_tickers)
    print("Calculating lags, moving averages, RSI/MACD and BTC correlations...")
    for metal in tickers.keys():
        # price-based features (lags, rolling stats, pct change)
        new_data[f"{metal}_Lag1"] = new_data[metal].shift(1)
        new_data[f"{metal}_Lag3"] = new_data[metal].shift(3)
        new_data[f"{metal}_MA7"] = new_data[metal].rolling(window=7).mean()
        new_data[f"{metal}_Pct_change"] = new_data[metal].pct_change()

        # momentum indicators
        new_data[f"{metal}_RSI_14"] = ta.rsi(new_data[metal], length=14)
        macd_vals = ta.macd(new_data[metal], fast=12, slow=26, signal=9)
        new_data[f"{metal}_MACD"] = macd_vals.get("MACD_12_26_9")

        # correlation with BTC only for commodities
        if metal != "BTC":
            new_data[f"{metal}_BTC_Corr"] = new_data[metal].rolling(window=14).corr(new_data["BTC"])

    # make sure old snapshot has any columns that the new data produces (after features)
    for col in new_data.columns:
        if col not in df_old.columns:
            df_old[col] = np.nan

    latest_row = new_data.tail(1).reset_index()
    new_date = pd.to_datetime(latest_row['Date'].iloc[0])

    # after ensuring df_old has the full column set, decide whether to append
    final_df = df_old
    if new_date > last_date_in_csv:
        # append the new row (latest_row already has a Date column)
        df_updated = pd.concat([df_old, latest_row], ignore_index=True)
        # ensure Date column remains first for readability
        if 'Date' in df_updated.columns:
            cols = df_updated.columns.tolist()
            cols.insert(0, cols.pop(cols.index('Date')))
            df_updated = df_updated[cols]
        final_df = df_updated
        print(f"Added new data for {new_date.date()} to snapshot.")
    else:
        print(f"No new data to add. Latest date in snapshot: {last_date_in_csv.date()}")
    # write cleaned data back out so the CSV always has a consistent layout
    final_df.to_csv(csv_path, index=False)
    
    print("="*50)

if __name__ == "__main__":
    update_market_snapshot()
