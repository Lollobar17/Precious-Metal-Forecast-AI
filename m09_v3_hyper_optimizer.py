import optuna 
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

def v3_optimize_hyperparameters(df, target_asset):
    """
    Finds the best XGBoost parameters to maximise prediction accuracy for a specific metal (now including copper) using Bayesian Optimization (Optuna.)
    """
    print(f"\n>>> Running Hyperparameter Optimization for: {target_asset}")

    if target_asset not in df.columns:
        raise ValueError(f"Target asset '{target_asset}' not found in dataframe")

    df_opt = df.copy()
    # compute log return for the target, shift so we predict the *next* day
    df_opt['Target_Return'] = np.log(df_opt[target_asset] / df_opt[target_asset].shift(1)).shift(-1)
    # drop rows where the target or its return are NaN; this removes the first
    # row (no prior price) and final row (no forward return) as well as any gaps
    df_opt = df_opt.dropna(subset=[target_asset, 'Target_Return'])

    # include any lag, correlation, pct change or moving average features
    features = [col for col in df_opt.columns
                if any(key in col for key in ['Lag','Corr','Pct','MA','RSI'])]
    X = df_opt[features]
    y = df_opt['Target_Return']

    if X.shape[0] < 10:
        # not enough samples to run time‑series cross validation
        print(f"Not enough data ({X.shape[0]} rows) to optimize for {target_asset}, skipping.")
        return {}

    def objective(trial):

        params = {
            'n_estimators': trial.suggest_int('n_estimators', 200, 1500),
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.005, 0.2, log=True),
            'subsample': trial.suggest_float('subsample', 0.6, 0.9),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 0.9),
            'gamma': trial.suggest_float('gamma', 1e-5, 0.5, log=True),
            'objective': 'reg:squarederror',
            'random_state': 42,
            'n_jobs': -1
        }

        # adjust number of splits based on available observations
        n_splits = min(5, max(2, len(X) // 10))
        tscv = TimeSeriesSplit(n_splits=n_splits)
        correlations = []

        for train_idx, val_idx in tscv.split(X):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            model = xgb.XGBRegressor(**params)
            model.fit(X_train, y_train)
            preds = model.predict(X_val)

            if np.std(preds) == 0:
                score = -1
            else:
                score = np.corrcoef(y_val, preds)[0, 1]

            correlations.append(score if not np.isnan(score) else -1)
        
        return np.mean(correlations)

    study = optuna.create_study(direction='maximize')
    # allow caller to override number of trials via outer variable
    n_trials = globals().get("V3_OPT_TRIALS", 50)
    study.optimize(objective, n_trials=n_trials)
    print(f"DONE: Best Score for {target_asset}: {study.best_value:.4f}")

    best_params = study.best_params
    champion_model = xgb.XGBRegressor(**best_params)
    champion_model.fit(X, y)
    model_filename = f"model_v3_{target_asset.lower()}.json"
    champion_model.save_model(model_filename)
    print(f"Model saved: {model_filename}")
    return study.best_params

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Optimize hyperparameters for v3 metal models")
    parser.add_argument('--trials', type=int, default=50,
                        help='number of Optuna trials per asset (default 50)')
    args = parser.parse_args()

    # entry-point: iterate through assets and optimize
    df_market = pd.read_csv('v2_final_market_snapshot.csv')
    metals = ["Gold", "Silver", "Platinum", "Palladium", "Copper"]

    globals()["V3_OPT_TRIALS"] = args.trials

    for metal in metals:
        print("\n" + "="*50)
        print(f"\n V3 Optimization Start for: {metal.upper()}")
        print("="*50)
        best_p = v3_optimize_hyperparameters(df_market, metal)
        if best_p:
            print(f"Best parameters for {metal}: {best_p}\n")
    print("All optimizations complete.")