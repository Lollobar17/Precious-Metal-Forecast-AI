import pandas as pd  # noqa: F401
import xgboost as xgb
from sklearn.metrics import mean_squared_error, r2_score  # noqa: F401
import matplotlib.pyplot as plt

def v2_run_multi_metal_model(df):
    """
    Trains an XGBoost model to predict the price of gold, silver, platinum, palladium and copper
    using their historical data and correlations.
    """
    metals = ['Gold', 'Silver', 'Platinum', 'Palladium', 'Copper']
    all_results = {}
    print("--- Starting V2 Model Engine ---")
    print("Features used: Lags, Pct Changes, and Correlations with BTC")

    for target in metals:
        print(f"\n> Processing Model for: {target}...")

        df_model = df.copy()
        df_model['Target_Next_Day'] = df_model[target].shift(-1)
        df_model = df_model.dropna()
        # use any lag/correlation/pct-change/moving-average or RSI/MACD features
        features = [col for col in df_model.columns if any(k in col for k in ['Lag','Pct','Corr','MA','RSI','MACD'])]
        X = df_model[features]
        y = df_model['Target_Next_Day']
        split_index = int(len(df_model) * 0.8)
        X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
        y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

        model = xgb.XGBRegressor(
            n_estimators=500,
            learning_rate=0.1,
            max_depth=5,
            subsample=0.8,
            colsample_bytree=0.8,
            gamma=0.1,
            objective ='reg:squarederror',
            random_state=42
        )

        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        all_results[target] = (y_test, predictions)
        score = r2_score(y_test, predictions)
        print(f"Model accuracy (R^2 Score) for {target}: {score:.4f}")
        
    return all_results

def v2_plot_all_forecast(results):
    """Generates a comparison grid for all metals showing actual vs predicted prices."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    axes = axes.flatten()

    for i, (metal, data) in enumerate(results.items()):
        y_true, y_predictions = data
        axes[i].plot(y_true.index, y_true.values, label=f"Actual {metal} Price", color='#1f77b4', alpha=0.6, linewidth=2)
        axes[i].plot(y_true.index, y_predictions, label=f"AI {metal} Forecast Price", color='#ff7f0e', linestyle='--', linewidth=1.5)
        axes[i].set_title(f"Truth Test: {metal} vs BTC Correlation Model Price Forecast - V2 Model", fontsize=12)
        axes[i].set_ylabel("Price in USD", fontsize=12)
        axes[i].legend()
        axes[i].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # load data from CSV if available, otherwise exit
    try:
        df = pd.read_csv('v2_market_data.csv')
    except FileNotFoundError:
        print("Please run 5_v2_data_loader or provide a CSV path.")
        df = None
    if df is not None:
        forecast_results = v2_run_multi_metal_model(df)
        if forecast_results:
            v2_plot_all_forecast(forecast_results)
