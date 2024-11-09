import polars as pl

df = pl.read_csv("data_in.csv")

print(df)

# 选择前10行并保存
df.head(10).write_csv("data_out.csv")
