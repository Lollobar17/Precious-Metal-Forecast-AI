import pandas as pd
from datetime import datetime
import m5_v2_data_loader as loader
import m6_v2_model as model_engine
import m7_v2_backtester as backtester

def run_v2_integrated_system():
    print(f"{'='*50}")
    print(f"STARTING INTEGRATED TRADING SYSTEM V2 - {datetime.now().strftime('%Y-%m-%d')}")
    print(f"{'='*50}")
    print("\n[PHASE 1] Fetching and Synchronizing Market Data...")
    market_data = loader.v2_load_and_sync_data(period="5y")
    market_data.to_csv("v2_final_market_snapshot.csv")
    print(f"Successfully processed {len(market_data)} trading days.")
    print("\n[PHASE 2] Training the XGBoost Model with V2 Enhancements...")
    forecast_results = model_engine.v2_run_multi_metal_model(market_data)
    print("\n[PHASE 3] Running the Backtest for V2 Strategy...")
    strategy_reports = backtester.v2_run_backtest(forecast_results, threshold=0.0001)
    print("\n" +"="*30)
    print("    Final Performance Summary    ")
    print("\n" +"="*30)
    summary_data = []
    for metal, df in strategy_reports.items():
        final_return = df['Strategy_Equity'].iloc[-1]
        market_return = df['Market_Equity'].iloc[-1]
        strategy_std = df['Strategy_Returns'].std()
        sharpe = (df['Strategy_Returns'].mean() / strategy_std) * (252**0.5) if strategy_std != 0 else 0
        summary_data.append({
            'Asset': metal,
            'AI Return': f"{(final_return-1)*100:.2f}%",
            'Market Return': f"{(market_return-1)*100:.2f}%",
            'Sharpe Ratio': f"{sharpe:.2f}"
        })

    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    print("="*30)
    print("\n[PHASE 4] Plotting Forecasts and Backtest Results...")
    backtester.v2_plot_equity_curves(strategy_reports)

if __name__ == "__main__":
    try:
        run_v2_integrated_system()
    except Exception as e:
        print(f"An error occurred during execution: {e}")
        print("Tip: Check if the CSV file is open in another program of if tickers are correct.")