import os
import pandas as pd
import numpy as np
import xgboost as xgb
from m11_v4_live_updater import update_market_snapshot

def run_precious_metal_forecast():
    """
    V4 All-in-One Script:
    1. Updates the market snapshot with the latest data (now including copper).
    2. Loads the updated snapshot, trains an XGBoost model, and forecasts the next day's price for each metal.
    """

    update_market_snapshot()
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_path, 'v2_final_market_snapshot.csv')

    # load using the same path update_market_snapshot writes to
    # read the snapshot and parse index as datetime
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    # guarantee a timestamp object
    df.index = pd.to_datetime(df.index, errors='coerce')
    latest_row = df.tail(1)
    print(f"\nLoaded updated snapshot with {len(df)} records.")

    # list of assets to make forecasts for (now including copper)
    metals = ["Gold", "Silver", "Platinum", "Palladium", "Copper"]
    # we will not compute a global feature list here; instead each model's
    # expected features are inspected after loading so that older models (or
    # new ones trained with extra lags/MA) continue to work.

    print(f"\n{'='*40}")
    print(f"Forecast prevision V4 - {pd.Timestamp.now().strftime('%d/%m/%Y')}")
    print(f"{'='*40}")

    for m in metals:
        try:
            model = xgb.XGBRegressor()
            # construct filename relative to this script's directory
            model_file = os.path.join(base_path, f'model_v3_{m.lower()}.json')
            model.load_model(model_file)
            # pick only the columns the model was trained with (maintains
            # backwards compatibility when we add new features later)
            expected = model.get_booster().feature_names
            X = latest_row[expected]
            # model outputs a log-return; convert to price estimate
            log_return = model.predict(X)[0]
            current_price = latest_row[m.capitalize()].values[0]
            forecast_price = current_price * np.exp(log_return)
            change = ((forecast_price - current_price) / current_price) * 100
            print(f"{m}: Current Price = {current_price:.2f}, Forecasted Price = {forecast_price:.2f}, Change = {change:.2f}%")
            print("-" * 20)

        except Exception as e:
            print(f"Error forecasting for {m}: {e}")

if __name__ == "__main__":
    run_precious_metal_forecast()