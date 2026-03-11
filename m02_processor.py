import pandas as pd  # noqa: F401
import pandas_ta as ta



def add_indicators(df):
    print("Adding memory and indicators to the AI...")

    # calculate returns for gold and copper (if available)
    df['Gold_Returns'] = df['Gold'].pct_change()
    if 'Copper' in df.columns:
        df['Copper_Returns'] = df['Copper'].pct_change()
    
    df['RSI_14'] = ta.rsi(df['Gold'], length=14)
    df['SMA_20'] = ta.sma(df['Gold'], length=20)
    
    df['Lag_Return'] = df['Gold_Returns'].shift(1)
    
    df['Target_Return'] = df['Gold_Returns'].shift(-1)
    
    return df.dropna()