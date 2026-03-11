"""Quick retraining script: fit XGBoost regressor on the full snapshot
without searching hyperparameters. Useful when data has been updated and
previously learned parameters are still valid or when optimization is too slow.
"""
import pandas as pd
import numpy as np
import xgboost as xgb

def quick_retrain():
    """Perform a fast retrain over all metals using the current snapshot."""
    snapshot = pd.read_csv('v2_final_market_snapshot.csv')
    metals = ["Gold", "Silver", "Platinum", "Palladium", "Copper"]

    for metal in metals:
        if metal not in snapshot.columns:
            print(f"{metal} column missing from snapshot, skipping")
            continue
        df = snapshot.copy()
        df['Target_Return'] = np.log(df[metal] / df[metal].shift(1)).shift(-1)
        df = df.dropna(subset=[metal, 'Target_Return'])
        features = [col for col in df.columns
                    if any(key in col for key in ['Lag','Corr','Pct','MA','RSI'])]
        X = df[features]
        y = df['Target_Return']
        if X.shape[0] < 10:
            print(f"Not enough data for {metal}, skipping retrain")
            continue
        print(f"Retraining {metal} model on {X.shape[0]} samples")
        model = xgb.XGBRegressor(random_state=42, n_jobs=-1)
        model.fit(X, y)
        fname = f"model_v3_{metal.lower()}.json"
        model.save_model(fname)
        print(f"Saved {fname}")

    print("Quick retraining complete.")


if __name__ == '__main__':
    quick_retrain()
