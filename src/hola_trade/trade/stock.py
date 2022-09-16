import numpy as np
from typing import List
from hola_trade.core.ctx import Context, Bar


class Stock:
    def __init__(self, code: str) -> None:
        self.code = code

    def get_up_rate(self) -> float:
        return 1.2 if self.code[0] == '3' or self.code[:3] == '688' else 1.1

    def get_down_rate(self) -> float:
        return 0.8 if self.code[0] == '3' or self.code[:3] == '688' else 0.9

    # return pandas.Series
    def get_yest_data(self, ctx: Context, fields: List[str]):
        df = ctx.get_market_data(fields, self.code, days=2)
        return df.iloc[0]

    def get_yest_close(self, ctx: Context) -> float:
        return self.get_yest_data(ctx, ["close"])["close"]

    def get_price(self, ctx: Context) -> float:
        return ctx.get_price(self.code)

    def get_rate(self, ctx: Context) -> float:
        price = self.get_price(ctx)
        yest = self.get_yest_close(ctx)
        return round((price - yest) * 100 / yest, 2)

    def is_up(self, ctx: Context) -> bool:
        current_price = self.get_price(ctx)
        yest_close = self.get_yest_close(ctx)
        up_price = yest_close * self.get_up_rate()
        return abs(current_price - up_price) < 0.01

    def is_down(self, ctx: Context) -> bool:
        current_price = self.get_price(ctx)
        yest_close = self.get_yest_close(ctx)
        down_price = yest_close * self.get_down_rate()
        return abs(current_price - down_price) < 0.01

    def get_avg_amp(self, ctx: Context, days: int) -> float:
        df = ctx.get_market_data(["high", "low"], self.code, days)
        if len(df) == days:
            return np.mean((df["high"] - df["low"]) * 100 / df["low"])
        else:
            return 0

    def get_avg_price(self, ctx: Context, days: int) -> float:
        df = ctx.get_market_data(["close"], self.code, days)
        if len(df) == days:
            return np.mean(df["close"])
        else:
            return 0

    def get_amount_ratio(self, ctx: Context, bar: Bar) -> float:
        days = 5
        df = ctx.get_market_data(["amount"], self.code, days)
        if len(df) == days:
            avg = np.mean(df["amount"]) / 240
            amount = ctx.get_amount(self.code)
            minutes = bar.get_open_seconds(ctx) // 60
            if minutes > 0:
                return round((amount/minutes)/avg, 2)

        return 0

    # how many days, return Optional[Series], must check None
    def get_rolling_avg_price(self, ctx: Context, window: int, days: int):
        df = ctx.get_market_data(["close"], self.code, days + window)
        if len(df) == days:
            return df.rolling(window=window).mean[days*-1:]["close"]
        else:
            return None

    # return Optional[Series], must check None
    def get_prices(self, ctx: Context, days: int):
        df = ctx.get_market_data(["close"], self.code, days)
        if len(df) == days:
            return df["close"]
        else:
            return None

    # return Optional[Series], must check None
    def get_history(self, ctx: Context, fields: List[str], days: int):
        df = ctx.get_market_data(fields, self.code, days)
        if len(df) == days:
            return df
        else:
            return None
