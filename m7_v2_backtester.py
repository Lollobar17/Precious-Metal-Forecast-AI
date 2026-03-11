import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def v2_run_backtest(forecast_results, threshold=0.005):
    """
    Simulates a trading strategy based on the AI model's predictions and evaluates its performance.
    Logic:
    - BUY if the predicted return is above the threshold (indicating a strong positive trend).
    - HOLD/FLAT if the predicted return is between -threshold and threshold (indicating a neutral trend).
    """
    backtest_reports = {}
    print("\n--- Starting V2 Strategy Backtest (Truth Test) ---")

    for metal, (y_true, y_predictions) in forecast_results.items():
        df_bt = pd.DataFrame({
            'Actual_Price': y_true,
            'Predicted_Price': y_predictions
        }, index=y_true.index)

        df_bt['Signal'] = np.where(
            df_bt['Predicted_Price'] > df_bt['Actual_Price'] * (1 + threshold), 
            1, 0
        )

        df_bt['Market_Returns'] = df_bt['Actual_Price'].pct_change()
        df_bt['Strategy_Returns'] = df_bt['Signal'].shift(1) * df_bt['Market_Returns']
        df_bt['Market_Equity'] = (1 + df_bt['Market_Returns'].fillna(0)).cumprod()
        df_bt['Strategy_Equity'] = (1 + df_bt['Strategy_Returns'].fillna(0)).cumprod()
        final_return = df_bt['Strategy_Equity'].iloc[-1]
        sharpe = (df_bt['Strategy_Returns'].mean() / df_bt['Strategy_Returns'].std()) * np.sqrt(252) if df_bt['Strategy_Returns'].std() != 0 else 0
        
        print(f"[{metal}] Final Equity: {final_return:.2f}x | Sharpe Ratio: {sharpe:.2f}")
        backtest_reports[metal] = df_bt
    
    return backtest_reports

def v2_plot_equity_curves(backtest_reports):
    """Plots the performance of the AI Strategy vs Buy & Hold for each metal."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    axes = axes.flatten()

    for i, (metal, df) in enumerate(backtest_reports.items()):
        df_bt = df
        axes[i].plot(df_bt.index, df_bt['Market_Equity'], label=f"Buy & Hold {metal}", color='gray', alpha=0.3)
        axes[i].plot(df_bt.index, df_bt['Strategy_Equity'], label=f"AI V2 Strategy {metal}", color='#2ca02c', linestyle='--', linewidth=1.5)
        axes[i].set_title(f"Backtest Equity Curve: {metal} - V2 Strategy Backtest", fontsize=12, fontweight='bold', pad=15)
        axes[i].set_ylabel("Equity Growth (x)", fontsize=10)
        axes[i].legend(loc='upper left', fontsize='small')
        axes[i].grid(True, alpha=0.2)
    
    plt.subplots_adjust(top=0.94, bottom=0.12, hspace=0.6, wspace=0.25)
    plt.tight_layout(rect=[0.02, 0.08, 1, 0.96])

    for ax in axes:
        ax.title.set_size(10)
        ax.title.set_position([.5, 1.05])

    plt.suptitle("V2 Performance: AI vs Market", fontsize=16, y=0.98, fontweight='bold')
    plt.show()

if __name__ == "__main__":
    print("V2 Backtester module executed. Integrate this with m6_v2_model.py in m4_main.py")