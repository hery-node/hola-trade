import numpy as np
import pandas as pd
from typing import List
from hola_trade.core.ctx import Context, Bar
from hola_trade.trade.condition import Target


class Stock:
    def __init__(self, code: str) -> None:
        self.code = code

    def get_up_rate(self) -> float:
        return 1.2 if self.code[0] == '3' or self.code[:3] == '688' else 1.1

    def get_down_rate(self) -> float:
        return 0.8 if self.code[0] == '3' or self.code[:3] == '688' else 0.9

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

    # return pandas.Series
    def get_yest_data(self, ctx: Context, fields: List[str]):
        df = ctx.get_market_data(fields, self.code, days=2)
        return df.iloc[0]

    def get_yest_close(self, ctx: Context) -> float:
        field = "close"
        close = self.get_yest_data(ctx, [field])[field]
        return round(close, 2)

    def get_price(self, ctx: Context) -> float:
        return round(ctx.get_price(self.code), 2)

    def get_rate(self, ctx: Context) -> float:
        price = self.get_price(ctx)
        yest = self.get_yest_close(ctx)
        return round((price - yest) * 100 / yest, 2)

    def get_open(self, ctx: Context, bar: Bar) -> float:
        field = "open"
        open_time = bar.get_bar_open_str_time(ctx)
        return round(ctx.get_field(self.code, field, open_time), 2)

    def get_high(self, ctx: Context, bar: Bar) -> float:
        field = "high"
        open_time = bar.get_bar_open_str_time(ctx)
        return round(ctx.get_field(self.code, field, open_time), 2)

    def get_low(self, ctx: Context, bar: Bar) -> float:
        field = "low"
        open_time = bar.get_bar_open_str_time(ctx)
        return round(ctx.get_field(self.code, field, open_time), 2)

    def get_amount(self, ctx: Context, bar: Bar) -> float:
        field = "amount"
        open_time = bar.get_bar_open_str_time(ctx)
        return round(ctx.get_field(self.code, field, open_time), 2)

    def get_volume(self, ctx: Context, bar: Bar) -> int:
        field = "volume"
        open_time = bar.get_bar_open_str_time(ctx)
        return int(ctx.get_field(self.code, field, open_time))

    def get_amount_ratio(self, ctx: Context, bar: Bar) -> float:
        days = 6
        field = "amount"
        df = ctx.get_market_data([field], self.code, days)
        if len(df) == days:
            avg = np.mean(df[field][:-1]) / 240
            amount = self.get_amount(ctx, bar)
            minutes = bar.get_open_seconds(ctx) // 60
            if minutes > 0:
                return round((amount/minutes)/avg, 2)
        return 0

    # avg amp, using previous days, not including today
    def get_avg_amp(self, ctx: Context, days: int) -> float:
        days = days + 1
        df = ctx.get_market_data(["high", "low"], self.code, days)
        if len(df) == days:
            df = df[:-1]
            return round(np.mean((df["high"] - df["low"]) * 100 / df["low"]), 2)
        else:
            return 0

    # return Series, must check length, including today
    def get_prices(self, ctx: Context, days: int):
        field = "close"
        df = ctx.get_market_data([field], self.code, days)
        if len(df) == days:
            if ctx.do_back_test():
                df.iat[-1, 0] = self.get_price(ctx)
            return df[field]
        else:
            return pd.Series(dtype=float)

    # avg price, including today
    def get_avg_price(self, ctx: Context, days: int) -> float:
        prices = self.get_prices(ctx, days)
        if len(prices) > 0:
            return round(np.mean(prices), 2)
        else:
            return 0

    # avg price, including today
    def get_rolling_avg_price(self, ctx: Context, window: int, days: int):
        # how many days, return Series, must check length
        field = "close"
        period = days + window
        prices = self.get_prices(ctx, period)
        if len(prices) == period:
            return prices.rolling(window=window).mean[days * -1:][field]
        else:
            return pd.Series(dtype=float)

    # return Dataframe, must check length, not including today
    def get_history(self, ctx: Context, fields: List[str], days: int):
        days = days + 1
        df = ctx.get_market_data(fields, self.code, days)
        if len(df) == days:
            return df[:-1]
        else:
            return pd.DataFrame()

    # return Dataframe, not including today
    def get_history_from_start(self, ctx: Context, fields: List[str], start_time: str):
        df = ctx.get_market_data_from_start(fields, self.code, start_time)
        return df[:-1]

    # not including today
    def get_high_in_days(self, ctx: Context, days: int) -> float:
        field = "high"
        df = self.get_history(ctx, [field], days)
        if len(df) > 0:
            return round(np.max(df[field]), 2)
        else:
            return 0

    # not including today
    def get_high_from_start(self, ctx: Context, start_time: str) -> float:
        field = "high"
        df = self.get_history_from_start(ctx, [field], start_time)
        if len(df) > 0:
            return round(np.max(df[field]), 2)
        else:
            return 0

    # not including today
    def get_low_in_days(self, ctx: Context, days: int) -> float:
        field = "low"
        df = self.get_history(ctx, [field], days)
        if len(df) > 0:
            return round(np.min(df[field]), 2)
        else:
            return 0

   # not including today
    def get_low_from_start(self, ctx: Context, start_time: str) -> float:
        field = "low"
        df = self.get_history_from_start(ctx, [field], start_time)
        if len(df) > 0:
            return round(np.min(df[field]), 2)
        else:
            return 0


class BatchStock:
    # this is used for select condition to boost performance
    def __init__(self, codes: List[str]) -> None:
        if len(codes) > 1:
            self.codes = codes
        else:
            raise ValueError("using stock instead of BatchStock")

    # use history data, not including today
    def below_long_price(self, ctx: Context, window: int, watch_days: int, watch_ratio: float) -> List[Target]:
        field = "close"
        panel = ctx.batch_get_market_data([field], self.codes, watch_days + window + 1)
        results = []
        for code in self.codes:
            df = panel[code]
            prices = df[watch_days*-1 - 1:-1][field]
            slow_prices = df.rolling(window=window).mean[watch_days*-1 - 1:-1][field]
            diffs = (prices/slow_prices).tolist()
            meet_days = len([diff for diff in diffs if diff < 1])
            if (meet_days/watch_days) > watch_ratio:
                results.append(Target(code, 0))
        return results
