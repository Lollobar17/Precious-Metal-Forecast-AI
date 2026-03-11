# Precious Metal Forecast Workspace

This repository contains a series of Python scripts for downloading market data, engineering features, training machine learning models, backtesting strategies and generating forecasts for precious metals. The code has evolved through several versions; the files are arranged by version and purpose. A requirements file (`m0_requirements.txt`) lists the necessary Python packages.

## File Organization & Logical Order

1. **Core utilities & notebook scripts (legacy)**
- `m1_data_loader.py` – simple downloader for Gold/Copper etc.
- `m2_processor.py` – add technical indicators (RSI, SMA).
- `m3_model.py` – train a basic XGBoost model on processed data.
- `m4_main.py` – orchestrates the m1–m3 workflow and plots results.

2. **Version 2: multi‑metal pipeline with backtesting**
- `m5_v2_data_loader.py` – downloads and synchronises five metals plus BTC.
- `m6_v2_model.py` – trains separate models for each metal, uses enhanced features.
- `m7_v2_backtester.py` – simulates a trading strategy and plots equity curves.
- `m8_v2_main.py` – integrated system that runs the full V2 pipeline end‑to-end.

3. **Version 3: hyperparameter optimisation & modular forecasting**
- `m9_v3_hyper_optimizer.py` – Optuna‑based search for best XGBoost parameters.
- `m10_v3_forecaster.py` – loads saved v3 models and produces daily price forecasts.

4. **Version 4: live updater & all‑in‑one runner**
- `m11_v4_live_updater.py` – refreshes the market snapshot with new data and features.
- `m12_v4_all_in_one.py` – combines updater and forecaster into a single daily script.

5. **Telegram Bot Integration**
- `m17_telegram_bridge.py` – Telegram bot for interactive forecasts and notifications.

6. **Helpers & orchestration**
   - `m13_rebuild_snapshot.py` – rebuilds the full historical snapshot from scratch.
   - `m14_retrain_models.py` – quick retrain of models without optimisation.
   - `m15_run_full_retrain.py` – wrapper that optionally rebuilds snapshot, retrains, and/or runs hyper‑optimizer.
   - `m16_inspect_snapshot.py` – utility to inspect the contents of the snapshot file.

7. **Data & outputs**
   - `data/` – CSV files downloaded by the scripts (`gold_data.csv` etc).
   - `v2_final_market_snapshot.csv` – the main market snapshot used by later versions.

## Telegram Bot Commands

The bot supports the following commands:

### Forecast Commands
| Command | Description |
|---------|-------------|
| `/start` or `/help` | Show welcome message with all commands |
| `/forecast <metal>` | Get price forecast for a specific metal |
| `/all` | Get all metal forecasts at once |
| `/dailyforecast` | Get immediate forecast and enable 9AM daily notifications |

### Price & Signal Commands
| Command | Description |
|---------|-------------|
| `/price <metal>` | Get current price for a metal |
| `/signal <metal>` | Get trading signal (Long/Short) |
| `/trend <metal>` | Get trend analysis with bullish/bearish indicator |
| `/market` | Get market overview with all metals |
| `/compare <metal1> <metal2>` | Compare two metals side by side |
| `/volatility` | View volatility data for all metals |
| `/history <metal> <days>` | View historical data (default 7 days) |

### Notification Commands
| Command | Description |
|---------|-------------|
| `/notify on` | Enable daily notifications (24h interval) |
| `/notify off` | Disable daily notifications |
| `/alerts <metal> <price>` | Set a price alert for a metal |
| `/myalerts` | View all your active alerts |
| `/deletealert <id>` | Delete a specific alert |

### Settings & Utilities
| Command | Description |
|---------|-------------|
| `/settings` | View your current settings and preferences |
| `/export` | Export data in text format |
| `/export json` | Export data in JSON format |
| `/ping` | Check bot response time |
| `/status` | Check if bot is running |
| `/stop` | Unsubscribe and clear all your data |
| `/auth` | Authorize your Telegram account |

### Supported Metals
- gold, silver, platinum, palladium, copper

## JSON Data Files

The Telegram bot uses the following JSON files for data persistence:

| File | Description |
|------|-------------|
| `bot_users.json` | List of authorized user Telegram IDs |
| `bot_notify.json` | User preferences for daily notifications |
| `bot_alerts.json` | User-created price alerts |
| `bot_daily_forecast.json` | User preferences for 9AM daily forecasts |

## Typical Workflows

* **Quick start**: run `python m4_main.py` to execute the original gold‑only forecasting system.
* **Version 2 analysis**: execute `python m8_v2_main.py` to download, model, backtest across multiple metals.
* **Retraining/optimisation**: use `python m15_run_full_retrain.py` followed by `python m10_v3_forecaster.py` or `python m12_v4_all_in_one.py` for daily forecasts.
* **Manual maintenance**: use `python m11_v4_live_updater.py` to refresh the snapshot or `python m13_rebuild_snapshot.py` when data corruption occurs.
* **Telegram Bot**: run `python m17_telegram_bridge.py` to start the Telegram bot for interactive forecasts. Use `/start` to see all commands, `/dailyforecast` to receive daily 9AM forecasts.

---

All files have been checked for syntax issues, unused imports and minor typos.

