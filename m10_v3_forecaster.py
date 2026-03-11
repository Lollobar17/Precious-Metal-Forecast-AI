import pandas as pd
import numpy as np
import xgboost as xgb
import os

def get_latest_forecast(model_file):
    """
    Get the latest forecast for a specific metal model.
    
    Args:
        model_file: The filename of the model JSON file (e.g., 'model_v3_gold.json')
    
    Returns:
        str: Formatted forecast message with price and signal
    """
    file_path = 'v2_final_market_snapshot.csv'
    if not os.path.exists(file_path):
        return f"Error: {file_path} not found!"
    
    df = pd.read_csv(file_path)
    latest_row = df.tail(1).copy()
    snapshot_date = latest_row['Date'].values[0]
    
    # Determine asset name from model file
    asset_name = None
    for metal in ['gold', 'silver', 'platinum', 'palladium', 'copper']:
        if metal in model_file.lower():
            asset_name = metal.capitalize()
            break
    
    if asset_name is None:
        return "Could not determine metal type from model file."
    
    # Find the model file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, model_file)
    
    if not os.path.exists(model_path):
        return f"Model file {model_file} not found!"
    
    try:
        model = xgb.XGBRegressor()
        model.load_model(model_path)
        expected = model.get_booster().feature_names
        X_input = latest_row[expected]
        log_return = model.predict(X_input)[0]
        current_price = latest_row[asset_name].values[0]
        forecast_price = current_price * np.exp(log_return)
        signal = "📈 Long" if log_return > 0 else "📉 Short"
        
        result = (f"📊 *{asset_name} Price Forecast*\n"
                  f"━━━━━━━━━━━━━━━━━━━━━\n"
                  f"📅 Date: {snapshot_date}\n"
                  f"💰 Current Price: ${current_price:.2f}\n"
                  f"🎯 Forecast Price: ${forecast_price:.2f}\n"
                  f"🔔 Signal: {signal}\n"
                  f"📈 Log Return: {log_return:.6f}")
        return result
    except Exception as e:
        return f"Error generating forecast: {str(e)}"


def run_v3_forecast():
    """
    Load saved XGBoost models and generate daily forecasts for Gold, Silver, Platinum, Palladium and Copper using the latest market snapshot.
    """
    file_path = 'v2_final_market_snapshot.csv'
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found!")
        return

    df = pd.read_csv(file_path)
    latest_row = df.tail(1).copy()
    snapshot_date = latest_row['Date'].values[0]
    # we won't build a global features list; each model may expect a
    # different subset -- we'll apply that later
    X_input = None  # placeholder, computed after loading the model
    base_dir = os.path.dirname(os.path.abspath(__file__))
    assets = ["Gold", "Silver", "Platinum", "Palladium", "Copper"]

    print("\n" + "="*60)
    print("Precious Metal Forecast v3 - Daily Report")
    print(f"Snapshot Date: {snapshot_date}")
    print("="*60)
    print(f"{'Asset':<12} | {'Forecast Price':<18} | {'Signal'}")
    # debug-info removed
    print("="*60)

    for asset in assets:
        target_name = asset.lower()
        found_file = None 

        for file in os.listdir(base_dir):
            if target_name in file.lower() and file.endswith(".json"):
                found_file = os.path.join(base_dir, file)
                break

        if found_file:
            model = xgb.XGBRegressor()
            model.load_model(found_file)
            expected = model.get_booster().feature_names
            X_input = latest_row[expected]
            log_return = model.predict(X_input)[0]
            current_price = latest_row[asset].values[0]
            forecast_price = current_price * np.exp(log_return)
            signal = "Long" if log_return > 0 else "Short"
            print(f"{asset:<12} | {forecast_price:>17.2f} | {signal}")
        else:
            print(f"{asset:<12} | Not found even as .json.json")

    print("-" * 60)
    print("Note: Prediction refer to the expected Log-Return for tomorrow's close.")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_v3_forecast()
