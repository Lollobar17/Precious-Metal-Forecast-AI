import telebot
from m10_v3_forecaster import get_latest_forecast
import json
import os
import threading
import time
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
# Note: Create a .env file with TELEGRAM_BOT_TOKEN=your_token before uploading 
try:
    load_dotenv()
except NameError:
    print("Warning: python-dotenv not installed. Install with: pip install python-dotenv")

# Get token from environment variable (required)
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN not set!")
    print("Please create a .env file with TELEGRAM_BOT_TOKEN=your_token or set the environment variable.")
    print("Get your token from @BotFather on Telegram.")
    exit(1)

# File to store authorized users
USER_DATA_FILE = 'bot_users.json'
NOTIFY_DATA_FILE = 'bot_notify.json'
ALERTS_DATA_FILE = 'bot_alerts.json'
DAILY_FORECAST_FILE = 'bot_daily_forecast.json'

def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return []

def save_users(users):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f)

def load_notify_settings():
    if os.path.exists(NOTIFY_DATA_FILE):
        with open(NOTIFY_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_notify_settings(settings):
    with open(NOTIFY_DATA_FILE, 'w') as f:
        json.dump(settings, f)

def load_alerts():
    if os.path.exists(ALERTS_DATA_FILE):
        with open(ALERTS_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_alerts(alerts):
    with open(ALERTS_DATA_FILE, 'w') as f:
        json.dump(alerts, f)

def load_daily_forecast_settings():
    if os.path.exists(DAILY_FORECAST_FILE):
        with open(DAILY_FORECAST_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_daily_forecast_settings(settings):
    with open(DAILY_FORECAST_FILE, 'w') as f:
        json.dump(settings, f)

authorized_users = load_users()
notify_settings = load_notify_settings()
alerts = load_alerts()
daily_forecast_settings = load_daily_forecast_settings()
bot = telebot.TeleBot(TOKEN)

METALS_FILE = {
    'gold': 'model_v3_gold.json',
    'silver': 'model_v3_silver.json',
    'platinum': 'model_v3_platinum.json',
    'palladium': 'model_v3_palladium.json',
    'copper': 'model_v3_copper.json'
}

def get_all_forecasts_message():
    """Generate a formatted message with all metal forecasts"""
    result = "*Daily Metal Forecasts*\n\n"
    for metal, model_file in METALS_FILE.items():
        try:
            forecast = get_latest_forecast(model_file)
            lines = forecast.split('\n')
            current = forecast_price = signal = "N/A"
            for line in lines:
                if 'Current Price:' in line:
                    current = line.split(': $', 1)[1] if ': $' in line else line.split(': ', 1)[1]
                elif 'Forecast Price:' in line:
                    forecast_price = line.split(': $', 1)[1] if ': $' in line else line.split(': ', 1)[1]
                elif 'Signal:' in line:
                    signal = line.split(': ', 1)[1]
            result += f"*{metal.capitalize()}*: ${current} → ${forecast_price} ({signal})\n"
        except Exception as e:
            result += f"*{metal.capitalize()}*: Error - {str(e)}\n"
    return result

@bot.message_handler(commands=['auth'])
def authorize_user(message):
    chat_id = message.chat.id
    if chat_id not in authorized_users:
        authorized_users.append(chat_id)
        save_users(authorized_users)
        bot.reply_to(message, "*You are now authorized!*", parse_mode='Markdown')
    else:
        bot.reply_to(message, "*You are already authorized*", parse_mode='Markdown')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = ("*Welcome to the Metal Price Forecast Bot!*\n\n"
                    "📊 *Forecast Commands:*\n"
                    "/forecast <metal> - Get price forecast for a metal\n"
                    "/all - Get all metal forecasts\n"
                    "/dailyforecast - Get daily forecast (schedules 9AM daily)\n\n"
                    "💰 *Price & Signal Commands:*\n"
                    "/price <metal> - Get current price\n"
                    "/signal <metal> - Get trading signal\n"
                    "/trend <metal> - Get trend analysis\n"
                    "/market - Get market overview\n"
                    "/compare <metal1> <metal2> - Compare two metals\n"
                    "/volatility - View volatility data\n"
                    "/history <metal> <days> - View historical data\n\n"
                    "🔔 *Notification Commands:*\n"
                    "/notify on - Enable daily notifications\n"
                    "/notify off - Disable daily notifications\n"
                    "/alerts <metal> <price> - Set price alert\n"
                    "/myalerts - View your alerts\n"
                    "/deletealert <id> - Delete an alert\n\n"
                    "⚙️ *Settings & Utilities:*\n"
                    "/settings - View your settings\n"
                    "/export - Export data\n"
                    "/ping - Check bot response time\n"
                    "/status - Check bot status\n"
                    "/stop - Unsubscribe and clear data\n\n"
                    "Available metals: gold, silver, platinum, palladium, copper.")
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

@bot.message_handler(commands=['forecast'])
def handle_forecast(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Please specify a metal. Usage: /forecast <metal>", parse_mode='Markdown')
            return

        metal = args[1].lower()
        if metal in METALS_FILE:
            result = get_latest_forecast(METALS_FILE[metal])
            bot.reply_to(message, result, parse_mode='Markdown')
        else:
            bot.reply_to(message, f"Unknown metal '{metal}'. Available metals: gold, silver, platinum, palladium, copper.", parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"An error occurred while processing your request: {str(e)}")

@bot.message_handler(commands=['status'])
def check_status(message):
    bot.reply_to(message, "Bot is running and ready to provide forecasts!", parse_mode='Markdown')

@bot.message_handler(commands=['all'])
def handle_all_forecasts(message):
    try:
        result = "*All Metal Forecasts*\n\n"
        for metal, model_file in METALS_FILE.items():
            forecast = get_latest_forecast(model_file)
            lines = forecast.split('\n')
            for line in lines:
                if 'Forecast Price:' in line:
                    result += f"*{metal.capitalize()}*: {line.split(': ', 1)[1]}\n"
                    break
            else:
                result += f"*{metal.capitalize()}*: Error\n"

        bot.reply_to(message, result, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")

@bot.message_handler(commands=['dailyforecast'])
def handle_dailyforecast(message):
    """Send daily forecast immediately and schedule for 9AM daily"""
    chat_id = str(message.chat.id)
    
    # Enable daily forecast for this user
    daily_forecast_settings[chat_id] = True
    save_daily_forecast_settings(daily_forecast_settings)
    
    # Send immediate forecast
    try:
        result = get_all_forecasts_message()
        result += "\n✅ *Daily forecast enabled!* You will receive forecasts at 9AM daily."
        bot.reply_to(message, result, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['notify'])
def handle_notify(message):
    chat_id = message.chat.id
    args = message.text.split()
    
    if len(args) < 2:
        is_enabled = notify_settings.get(str(chat_id), False)
        status = "enabled" if is_enabled else "disabled"
        bot.reply_to(message, f"Daily notifications are currently {status}\n\nUse /notify on to enable\nUse /notify off to disable", parse_mode='Markdown')
        return
    
    action = args[1].lower()
    if action == "on":
        notify_settings[str(chat_id)] = True
        save_notify_settings(notify_settings)
        bot.reply_to(message, "Daily notifications enabled!", parse_mode='Markdown')
    elif action == "off":
        notify_settings[str(chat_id)] = False
        save_notify_settings(notify_settings)
        bot.reply_to(message, "Daily notifications disabled", parse_mode='Markdown')
    else:
        bot.reply_to(message, "Use /notify on or /notify off", parse_mode='Markdown')

@bot.message_handler(commands=['price'])
def handle_price(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Usage: /price <metal>\nExample: /price gold", parse_mode='Markdown')
            return
        metal = args[1].lower()
        if metal not in METALS_FILE:
            bot.reply_to(message, "Unknown metal. Available: gold, silver, platinum, palladium, copper.", parse_mode='Markdown')
            return
        forecast = get_latest_forecast(METALS_FILE[metal])
        lines = forecast.split('\n')
        current_price = "N/A"
        for line in lines:
            if 'Current Price:' in line:
                current_price = line.split(': $', 1)[1] if ': $' in line else line.split(': ', 1)[1]
                break
        bot.reply_to(message, f"{metal.capitalize()} Current Price: ${current_price}", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['signal'])
def handle_signal(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Usage: /signal <metal>\nExample: /signal gold", parse_mode='Markdown')
            return
        metal = args[1].lower()
        if metal not in METALS_FILE:
            bot.reply_to(message, "Unknown metal. Available: gold, silver, platinum, palladium, copper.", parse_mode='Markdown')
            return
        forecast = get_latest_forecast(METALS_FILE[metal])
        lines = forecast.split('\n')
        signal = "N/A"
        for line in lines:
            if 'Signal:' in line:
                signal = line.split(': ', 1)[1]
                break
        bot.reply_to(message, f"{metal.capitalize()} Signal: {signal}", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['alerts'])
def handle_alerts(message):
    chat_id = str(message.chat.id)
    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "Usage: /alerts <metal> <price>\nExample: /alerts gold 2000", parse_mode='Markdown')
        return
    metal = args[1].lower()
    try:
        target_price = float(args[2])
    except ValueError:
        bot.reply_to(message, "Please enter a valid price number.", parse_mode='Markdown')
        return
    if metal not in METALS_FILE:
        bot.reply_to(message, "Unknown metal. Available: gold, silver, platinum, palladium, copper.", parse_mode='Markdown')
        return
    if chat_id not in alerts:
        alerts[chat_id] = []
    alert_id = len(alerts[chat_id]) + 1
    alerts[chat_id].append({"id": alert_id, "metal": metal, "target": target_price})
    save_alerts(alerts)
    bot.reply_to(message, f"Alert set! ID: {alert_id}\n{metal.capitalize()} at ${target_price}", parse_mode='Markdown')

@bot.message_handler(commands=['myalerts'])
def handle_myalerts(message):
    chat_id = str(message.chat.id)
    user_alerts = alerts.get(chat_id, [])
    if not user_alerts:
        bot.reply_to(message, "You have no active alerts.\nUse /alerts <metal> <price> to create one.", parse_mode='Markdown')
        return
    result = "Your Active Alerts:\n\n"
    for alert in user_alerts:
        result += f"ID {alert['id']}: {alert['metal'].capitalize()} at ${alert['target']}\n"
    bot.reply_to(message, result, parse_mode='Markdown')

@bot.message_handler(commands=['deletealert'])
def handle_deletealert(message):
    chat_id = str(message.chat.id)
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /deletealert <id>\nUse /myalerts to see alert IDs.", parse_mode='Markdown')
        return
    try:
        alert_id = int(args[1])
    except ValueError:
        bot.reply_to(message, "Please provide a valid alert ID.", parse_mode='Markdown')
        return
    user_alerts = alerts.get(chat_id, [])
    alerts[chat_id] = [a for a in user_alerts if a['id'] != alert_id]
    save_alerts(alerts)
    bot.reply_to(message, f"Alert {alert_id} deleted.", parse_mode='Markdown')

@bot.message_handler(commands=['market'])
def handle_market(message):
    try:
        result = "Market Overview\n\n"
        for metal, model_file in METALS_FILE.items():
            forecast = get_latest_forecast(model_file)
            lines = forecast.split('\n')
            current = forecast_price = signal = "N/A"
            for line in lines:
                if 'Current Price:' in line:
                    current = line.split(': $', 1)[1] if ': $' in line else line.split(': ', 1)[1]
                elif 'Forecast Price:' in line:
                    forecast_price = line.split(': $', 1)[1] if ': $' in line else line.split(': ', 1)[1]
                elif 'Signal:' in line:
                    signal = line.split(': ', 1)[1]
            result += f"{metal.capitalize()}: ${current} | Forecast: ${forecast_price} | {signal}\n"
        bot.reply_to(message, result, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['trend'])
def handle_trend(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Usage: /trend <metal>\nExample: /trend gold", parse_mode='Markdown')
            return
        metal = args[1].lower()
        if metal not in METALS_FILE:
            bot.reply_to(message, "Unknown metal. Available: gold, silver, platinum, palladium, copper.", parse_mode='Markdown')
            return
        forecast = get_latest_forecast(METALS_FILE[metal])
        lines = forecast.split('\n')
        signal = log_return = "N/A"
        for line in lines:
            if 'Signal:' in line:
                signal = line.split(': ', 1)[1]
            elif 'Log Return:' in line:
                log_return = line.split(': ', 1)[1]
        trend = "Bullish" if "Long" in signal else "Bearish" if "Short" in signal else "Neutral"
        emoji = "UP" if trend == "Bullish" else "DOWN" if trend == "Bearish" else "SIDEWAYS"
        bot.reply_to(message, f"{metal.capitalize()} Trend: {trend} ({emoji})\nLog Return: {log_return}", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['compare'])
def handle_compare(message):
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "Usage: /compare <metal1> <metal2>\nExample: /compare gold silver", parse_mode='Markdown')
            return
        metal1, metal2 = args[1].lower(), args[2].lower()
        if metal1 not in METALS_FILE or metal2 not in METALS_FILE:
            bot.reply_to(message, "Unknown metal. Available: gold, silver, platinum, palladium, copper.", parse_mode='Markdown')
            return
        forecast1 = get_latest_forecast(METALS_FILE[metal1])
        forecast2 = get_latest_forecast(METALS_FILE[metal2])
        price1 = price2 = signal1 = signal2 = "N/A"
        for line in forecast1.split('\n'):
            if 'Current Price:' in line:
                price1 = line.split(': $', 1)[1] if ': $' in line else line.split(': ', 1)[1]
            elif 'Signal:' in line:
                signal1 = line.split(': ', 1)[1]
        for line in forecast2.split('\n'):
            if 'Current Price:' in line:
                price2 = line.split(': $', 1)[1] if ': $' in line else line.split(': ', 1)[1]
            elif 'Signal:' in line:
                signal2 = line.split(': ', 1)[1]
        result = f"Comparison: {metal1.capitalize()} vs {metal2.capitalize()}\n\n"
        result += f"{metal1.capitalize()}: ${price1} | {signal1}\n"
        result += f"{metal2.capitalize()}: ${price2} | {signal2}"
        bot.reply_to(message, result, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['history'])
def handle_history(message):
    try:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "Usage: /history <metal> <days>\nExample: /history gold 30\nDefaults to 7 days if not specified.", parse_mode='Markdown')
            return
        metal = args[1].lower()
        if metal not in METALS_FILE:
            bot.reply_to(message, "Unknown metal. Available: gold, silver, platinum, palladium, copper.", parse_mode='Markdown')
            return
        days = int(args[2]) if len(args) > 2 else 7
        file_path = 'v2_final_market_snapshot.csv'
        if not os.path.exists(file_path):
            bot.reply_to(message, "History data not available.", parse_mode='Markdown')
            return
        df = pd.read_csv(file_path)
        df = df.tail(days)
        result = f"{metal.capitalize()} Last {days} Days\n\n"
        for _, row in df.iterrows():
            date = row['Date']
            price = row[metal.capitalize()]
            result += f"{date}: ${price:.2f}\n"
        bot.reply_to(message, result, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['volatility'])
def handle_volatility(message):
    try:
        file_path = 'v2_final_market_snapshot.csv'
        if not os.path.exists(file_path):
            bot.reply_to(message, "Data not available.", parse_mode='Markdown')
            return
        df = pd.read_csv(file_path)
        result = "Volatility (Std Dev of Returns)\n\n"
        for metal in METALS_FILE.keys():
            prices = df[metal.capitalize()].dropna()
            returns = prices.pct_change().dropna()
            vol = returns.std() * 100
            bar = "#" * int(vol * 10)
            result += f"{metal.capitalize()}: {vol:.3f}% {bar}\n"
        bot.reply_to(message, result, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    chat_id = str(message.chat.id)
    if chat_id in authorized_users:
        authorized_users.remove(chat_id)
        save_users(authorized_users)
    notify_settings[chat_id] = False
    save_notify_settings(notify_settings)
    # Disable daily forecast
    if chat_id in daily_forecast_settings:
        daily_forecast_settings[chat_id] = False
        save_daily_forecast_settings(daily_forecast_settings)
    if chat_id in alerts:
        alerts[chat_id] = []
        save_alerts(alerts)
    bot.reply_to(message, "You have been unsubscribed and all data cleared.", parse_mode='Markdown')

@bot.message_handler(commands=['ping'])
def handle_ping(message):
    start = time.time()
    bot.reply_to(message, "Pong!")
    end = time.time()
    bot.edit_message_text(f"Pong! Response time: {(end-start)*1000:.0f}ms", message.chat.id, message.message_id + 1)

@bot.message_handler(commands=['export'])
def handle_export(message):
    try:
        args = message.text.split()
        fmt = args[1].lower() if len(args) > 1 else "text"
        data = {}
        for metal, model_file in METALS_FILE.items():
            forecast = get_latest_forecast(model_file)
            lines = forecast.split('\n')
            current = forecast_price = signal = log_return = "N/A"
            for line in lines:
                if 'Current Price:' in line:
                    current = line.split(': $', 1)[1] if ': $' in line else line.split(': ', 1)[1]
                elif 'Forecast Price:' in line:
                    forecast_price = line.split(': $', 1)[1] if ': $' in line else line.split(': ', 1)[1]
                elif 'Signal:' in line:
                    signal = line.split(': ', 1)[1]
                elif 'Log Return:' in line:
                    log_return = line.split(': ', 1)[1]
            data[metal] = {"current_price": current, "forecast_price": forecast_price, "signal": signal, "log_return": log_return}
        if fmt == "json":
            bot.reply_to(message, "```json\n" + json.dumps(data, indent=2) + "\n```", parse_mode='Markdown')
        else:
            result = "Export Data\n\n"
            for metal, vals in data.items():
                result += f"{metal.capitalize()}: {vals}\n"
            bot.reply_to(message, result, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

@bot.message_handler(commands=['settings'])
def handle_settings(message):
    chat_id = str(message.chat.id)
    notify = notify_settings.get(chat_id, False)
    daily_enabled = daily_forecast_settings.get(chat_id, False)
    user_alerts = alerts.get(chat_id, [])
    result = "Your Settings\n\n"
    result += f"Daily Notifications: {'On' if notify else 'Off'}\n"
    result += f"Daily 9AM Forecast: {'On' if daily_enabled else 'Off'}\n"
    result += f"Active Alerts: {len(user_alerts)}\n\n"
    result += "Commands:\n"
    result += "/notify on - Enable daily notifications\n"
    result += "/notify off - Disable daily notifications\n"
    result += "/dailyforecast - Enable 9AM daily forecast\n"
    result += "/alerts <metal> <price> - Create alert\n"
    result += "/stop - Unsubscribe all"
    bot.reply_to(message, result, parse_mode='Markdown')

def send_daily_forecasts():
    """Original notification thread - sends every 24 hours"""
    while True:
        try:
            for chat_id, enabled in notify_settings.items():
                if enabled:
                    result = "Daily Metal Forecasts\n\n"
                    for metal, model_file in METALS_FILE.items():
                        forecast = get_latest_forecast(model_file)
                        lines = forecast.split('\n')
                        for line in lines:
                            if 'Forecast Price:' in line:
                                result += f"{metal.capitalize()}: {line.split(': ', 1)[1]}\n"
                                break
                    bot.send_message(int(chat_id), result, parse_mode='Markdown')
        except Exception as e:
            print(f"Error sending notifications: {e}")
        time.sleep(86400)

def send_9am_forecast():
    """New thread that sends forecasts at exactly 9AM daily"""
    while True:
        try:
            now = datetime.now()
            # Calculate time until next 9AM
            target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now >= target_time:
                # If it's past 9AM today, schedule for tomorrow
                target_time += timedelta(days=1)
            
            seconds_until_9am = (target_time - now).total_seconds()
            time.sleep(seconds_until_9am)
            
            # Send to all users who have daily forecast enabled
            for chat_id, enabled in daily_forecast_settings.items():
                if enabled:
                    try:
                        result = get_all_forecasts_message()
                        bot.send_message(int(chat_id), result, parse_mode='Markdown')
                    except Exception as e:
                        print(f"Error sending 9AM forecast to {chat_id}: {e}")
        except Exception as e:
            print(f"Error in 9AM forecast thread: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

# Start both notification threads
notification_thread = threading.Thread(target=send_daily_forecasts, daemon=True)
notification_thread.start()

forecast_9am_thread = threading.Thread(target=send_9am_forecast, daemon=True)
forecast_9am_thread.start()
print("Starting Telegram bot...")
bot.infinity_polling()

