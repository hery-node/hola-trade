import numpy as np
from ctx_info import ContextInfo


class Stock:
    def __init__(self, code: str):
        self.code = code

    def get_up_rate(self) -> float:
        return 1.2 if self.code[0] == '3' or self.code[:3] == '688' else 1.1

    def get_down_rate(self) -> float:
        return 0.8 if self.code[0] == '3' or self.code[:3] == '688' else 0.9

    def get_yest_data(self, ctx_info: ContextInfo, fields: list[str]):
        df = ctx_info.get_market_data(fields, self.code, days=2)
        return df.iloc[0]

    def get_yest_close(self, ctx_info: ContextInfo) -> float:
        return self.get_yest_data(ctx_info, ["close"])["close"]

    def get_price(self, ctx_info: ContextInfo) -> float:
        return ctx_info.get_price(self.code)

    def is_up(self, ctx_info: ContextInfo) -> bool:
        current_price = self.get_price(ctx_info)
        yest_close = self.get_yest_close(ctx_info)
        up_price = yest_close * self.get_up_rate()
        return abs(current_price - up_price) < 0.01

    def is_down(self, ctx_info: ContextInfo) -> bool:
        current_price = self.get_price(ctx_info)
        yest_close = self.get_yest_close(ctx_info)
        down_price = yest_close * self.get_down_rate()
        return abs(current_price - down_price) < 0.01

    def get_avg_amp(self, ctx_info: ContextInfo, days: int) -> float:
        df = ctx_info.get_market_data(["high", "low"], self.code, days)
        return np.mean((df["high"] - df["low"]) * 100 / df["low"])

    def get_avg_price(self, ctx_info: ContextInfo, days: int) -> float:
        df = ctx_info.get_market_data(["close"], self.code, days)
        return np.mean(df["close"])
