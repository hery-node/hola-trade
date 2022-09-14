import numpy as np


class Stock:

    @classmethod
    def get_all_codes(cls, ContextInfo):
        return ContextInfo.get_stock_list_in_sector('沪深A股')

    def __init__(self, code):
        self.code = code

    def get_up_rate(self):
        return 1.2 if self.code[0] == '3' or self.code[:3] == '688' else 1.1

    def get_down_rate(self):
        return 0.8 if self.code[0] == '3' or self.code[:3] == '688' else 0.9

    def get_yest_data(self, ContextInfo, fields):
        df = ContextInfo.get_market_data(fields, stock_code=[self.code], period="1d", count=2)
        return df.iloc[0]

    def get_yest_close(self, ContextInfo):
        return self.get_yest_data(ContextInfo, ["close"])["close"]

    def get_price(self, ContextInfo):
        if ContextInfo.do_back_test:
            return ContextInfo.get_market_data(["close"], stock_code=[self.code])
        else:
            return ContextInfo.get_full_tick(stock_code=[self.code])[self.code]["lastPrice"]

    def is_up(self, ContextInfo):
        current_price = self.get_price(ContextInfo)
        yest_close = self.get_yest_close(ContextInfo)
        up_price = yest_close * self.get_up_rate()
        return abs(current_price - up_price) < 0.01

    def is_down(self, ContextInfo):
        current_price = self.get_price(ContextInfo)
        yest_close = self.get_yest_close(ContextInfo)
        down_price = yest_close * self.get_down_rate()
        return abs(current_price - down_price) < 0.01

    def get_avg_amp(self, ContextInfo, days):
        df = ContextInfo.get_market_data(["high", "low"], stock_code=[self.code], period="1d", count=days)
        return np.mean((df["high"] - df["low"]) * 100 / df["low"])

    def get_avg_price(self, ContextInfo, days):
        df = ContextInfo.get_market_data(["close"], stock_code=[self.code], period="1d", count=days)
        return np.mean(df["close"])
