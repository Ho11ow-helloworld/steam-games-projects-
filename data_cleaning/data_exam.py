import pandas as pd

df_raw = pd.read_csv("./data/raw/93182_steam_games.csv")
print("数据集形状：", df_raw.shape)
print(df_raw.dtypes)
print(df_raw.isna().sum())

