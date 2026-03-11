import pandas as pd


def inspect():
    path = r"c:\Users\MPC\Desktop\Python\precious_metal_forecast\v2_final_market_snapshot.csv"
    df = pd.read_csv(path)
    print('rows', df.shape[0])
    print('gold nonnull', df['Gold'].notna().sum())
    print(df[['Date','Gold']].head())
    print(df[['Date','Gold']].tail())


if __name__ == '__main__':
    inspect()
