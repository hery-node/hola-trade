import os
import numpy as np
import pandas as pd
from hola_trade.trade.stock import Stock
from typing import List


class StockDB:
    def __init__(self, codes: List[str], days: List[int] = [3, 8, 21, 233], watch_days: int = 10, smooth_threshod: int = 2, close_threshod: int = 3, close_watch_days: int = 40) -> None:
        self.codes = codes
        self.dates = []
        self.days = days
        self.short_day = days[1]
        self.mid_day = days[2]
        self.long_day = days[3]
        self.watch_days = watch_days
        self.smooth_threshod = smooth_threshod
        self.close_threshod = close_threshod
        self.close_watch_days = close_watch_days

    def from_cvs_to_parquet(self, data_dir: str, out_file: str) -> None:
        markets = ["SH", "SZ"]
        dfs = []
        for market in markets:
            root_dir = f"{data_dir}/{market}"
            for excel_name in os.listdir(root_dir):
                df = pd.read_csv(f"{root_dir}/{excel_name}")
                code = excel_name.replace("price_", "").replace(".csv", "")
                stock = Stock(code)
                if len(df) > 10:
                    df["code"] = f"{market}.{code}"
                    df["yest"] = df.shift()["close"]
                    df["volumn_yest"] = df.shift()["volumn"]
                    df.dropna(subset=["yest", "volumn_yest"], inplace=True)
                    for day in self.days:
                        if day == self.short_day or day == self.mid_day or day == self.long_day:
                            df[f"av{day-1}"] = round(df["close"].rolling(window=(day-1)).mean(), 2)
                        df[f"av{day}"] = round(df["close"].rolling(window=day).mean(), 2)
                    df.dropna(subset=[f"av{self.long_day}"], inplace=True)

                    if len(df) == 0:
                        continue

                    if len(df) > self.close_watch_days:
                        df["ls"] = df.apply(lambda x: 1 if abs((x[f"av{self.long_day}"] / x[f"av{self.short_day}"]) - 1) < self.close_threshod * 0.01 else 0, axis=1)
                        df["lm"] = df.apply(lambda x: 1 if abs((x[f"av{self.long_day}"] / x[f"av{self.mid_day}"]) - 1) < self.close_threshod * 0.01 else 0, axis=1)
                        df["lc"] = df.apply(lambda x: 1 if abs((x[f"av{self.long_day}"] / x["close"]) - 1) < self.close_threshod * 0.01 else 0, axis=1)
                        df["mc"] = df.apply(lambda x: 1 if abs((x[f"av{self.mid_day}"] / x["close"]) - 1) < self.close_threshod * 0.01 else 0, axis=1)
                        df[f"ls{self.close_watch_days}"] = df["ls"].rolling(window=self.close_watch_days).sum()
                        df[f"lm{self.close_watch_days}"] = df["lm"].rolling(window=self.close_watch_days).sum()
                        df[f"lc{self.close_watch_days}"] = df["lc"].rolling(window=self.close_watch_days).sum()
                        df[f"mc{self.close_watch_days}"] = df["mc"].rolling(window=self.close_watch_days).sum()

                    df["rate"] = round((df["close"] - df["yest"]) * 100 / df["yest"], 2)
                    df["amplitude"] = round((df["high"] - df["low"]) * 100 / df["yest"], 2)
                    df["smooth"] = df.apply(lambda x: 1 if abs(x["rate"]) <= self.smooth_threshod and abs(x["amplitude"]) < self.smooth_threshod else 0, axis=1)
                    df["fall"] = round((df["close"] - df["high"]) * 100 / df["high"], 2)
                    df["rise"] = round((df["close"] - df["low"]) * 100 / df["low"], 2)
                    df["vratio"] = round(df["volumn"] / df["volumn_yest"], 2)
                    df["up"] = df.apply(lambda x: 1 if abs(x["yest"] * stock.get_up_rate() - x["close"]) < 0.01 else 0, axis=1)
                    df["down"] = df.apply(lambda x: 1 if abs(x["yest"] * stock.get_down_rate() - x["close"]) < 0.01 else 0, axis=1)
                    df["strong"] = df.apply(lambda x: 1 if x["rate"] >= (stock.get_up_rate() - 1) * 100 * 0.8 else 0, axis=1)
                    df["weak"] = df.apply(lambda x: 1 if x["rate"] <= (stock.get_down_rate() - 1) * 100 * 0.8 else 0, axis=1)

                    if len(df) > self.watch_days:
                        df[f"up{self.watch_days}"] = df["up"].rolling(window=self.watch_days).sum()
                        df[f"down{self.watch_days}"] = df["down"].rolling(window=self.watch_days).sum()
                        df[f"strong{self.watch_days}"] = df["strong"].rolling(window=self.watch_days).sum()
                        df[f"weak{self.watch_days}"] = df["weak"].rolling(window=self.watch_days).sum()
                        df[f"smooth{self.watch_days}"] = df["smooth"].rolling(window=self.watch_days).sum()

                    dfs.append(df)

        df_all = pd.concat(dfs)
        df_all.set_index(["code", "timetag"], inplace=True, drop=False)
        df_all.to_parquet(out_file, compression='gzip')

    def read_db(self, data) -> None:
        df = pd.read_parquet(data)
        df.sort_index(axis=1, inplace=True)
        df.sort_index(axis=0, inplace=True)
        self.dates = df.loc["SH.000001", "timetag"].to_numpy().tolist()
        self.df = df
        print(len(self.dates))
        print(df.loc["SZ.002641", 20220923])


data = "/home/dev/data/stock.parquet.gzip"
db = StockDB([])
# db.from_cvs_to_parquet("/home/dev/data", data)
db.read_db(data)
