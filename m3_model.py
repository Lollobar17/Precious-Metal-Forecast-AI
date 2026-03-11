from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error

def train_model(df):
    """
    Trains the AI model to predict the price of gold
    """

    features=['Returns', 'USD_Index', 'S&P500', 'RSI_14', 'SMA_20', 'Lag_Return']
    X = df[features]
    y = df['Target_Return']

    split_index = int(len(df) * 0.8)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    print("\n--- Training the AI model (XGBoost) ---")

    model = XGBRegressor(n_estimators=300, learning_rate=0.03, max_depth=8)
    model.fit(X_train, y_train)

    predictions_returns = model.predict(X_test)
    error = mean_absolute_error(y_test, predictions_returns)

    print("Training complete.")
    print(f"Mean Absolute Error: ${error:.4f}")

    return model, X_test, y_test, predictions_returns