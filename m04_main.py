from m01_data_loader import download_data
from m02_processor import add_indicators
from m03_model import train_model
import matplotlib.pyplot as plt

def run_system():
    """
    Main function to execute the full market prediction workflow.
    """
    print("--- Starting Gold Forecast System --- \n")

    print("Step 1: Downloading market data from Yahoo Finance...")
    df_raw = download_data()

    print("\nStep 2: Calculating technical indicators (RSI, SMA)...")
    df_processed = add_indicators(df_raw)

    print("\nStep 3: Training the XGBoost AI model...")
    model, X_test, y_test, predictions = train_model(df_processed)

    features = ['Returns', 'USD_Index', 'S&P500', 'RSI_14', 'SMA_20', 'Lag_Return']
    last_data_point = df_processed[features].tail(1)
    tomorrow_return = model.predict(last_data_point)[0]

    last_price  = df_raw['Gold'].iloc[-1]
    tomorrow_price = last_price * (1 + tomorrow_return)


    print("\n" + "=*40")
    print(f"Gold Price Prediction for Tomorrow: $ {tomorrow_price:.2f}")
    print(f"Expected Trend: {tomorrow_return*100:.2f}%")

    print("\nStep 4: Generating the forecast chart...")
    actual_prices = df_raw['Gold'].iloc[-len(y_test):].values
    predicted_prices = actual_prices * (1 + predictions)

    plt.figure(figsize=(14, 7))
    plt.plot(actual_prices, label="Actual Gold Price", color='#2ecc71', linewidth=2)
    plt.plot(predicted_prices, label="AI Prediction", color='#e74c3c', linestyle='--', linewidth=2)
    plt.title("Advanced Gold Market Forecast - XGBoost Model", fontsize=16)
    plt.ylabel("Price in USD", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(df_raw['Gold'].min() - 50, df_raw['Gold'].max() + 50)
    plt.tight_layout()

    manager = plt.get_current_fig_manager()
    try:
        manager.window.state('zoomed')
    except Exception:
        pass

    print("\n System completed! Please check the chart window.")
    plt.show()

if __name__ == "__main__":
    try:
        run_system()
    except Exception as e:
        print(f"An error occurred during execution: {e}")
        print("Tip: Check if the CSV file is open in another program of if tickers are correct.")
