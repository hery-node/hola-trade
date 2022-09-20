import numpy as np
import pandas as pd
from typing import List
from datetime import datetime


class Setting:
    # 0, debug, 1:info, 2: warn, 3:error
    log_level = 0
    # 0, disable, 1: enable
    quick_trade = 1
    # default price mode,3：卖2价 4：卖1价 5:最新价, 6：买1价 12：涨跌停价 13：挂单价 14：对手价, other type check doc
    default_price_buy_mode = 5
    default_price_sell_mode = 14
    # 'LATEST'：最新  'HANG'：挂单 'COMPETE'：对手 'MARKET'：市价 'SALE5', 'SALE4', 'SALE3', 'SALE2', 'SALE1'：卖5-1价 'BUY1', 'BUY2', 'BUY3', 'BUY4', 'BUY5'：买1-5价
    default_price_target_style = "COMPETE"


class Container:
    def __init__(self, timetag_to_datetime, get_trade_detail_data, passorder, order_target_percent) -> None:
        self.timetag_to_datetime = timetag_to_datetime
        self.get_trade_detail_data = get_trade_detail_data
        self.passorder = passorder
        self.order_target_percent = order_target_percent


class Context:
    def __init__(self, ContextInfo) -> None:
        self.ContextInfo = ContextInfo

    def get_bar_timetag(self) -> int:
        return self.ContextInfo.get_bar_timetag(self.ContextInfo.barpos)

    def get_stock_list_in_sector(self, sector: str) -> List[str]:
        return self.ContextInfo.get_stock_list_in_sector(sector)

    # return DataFrame
    def get_market_data(self, fields: List[str], code: str, days: int):
        return self.ContextInfo.get_market_data(fields, stock_code=[code], skip_paused=False, period="1d", dividend_type='front_ratio', count=days).round(2)

     # return Panel
    def batch_get_market_data(self, fields: List[str], codes: List[str], days: int):
        return self.ContextInfo.get_market_data(fields, stock_code=codes, skip_paused=False, period="1d", dividend_type='front_ratio', count=days).round(2)

    # return DataFrame
    def get_market_data_from_start(self, fields: List[str], code: str, start_time: str):
        return self.ContextInfo.get_market_data(fields, stock_code=[code], start_time=start_time, skip_paused=False, period="1d", dividend_type='front_ratio').round(2)

    def __convert_local_data_to_dataframe(self, data):
        sorted_keys = sorted(data.keys())
        data_list = [data[i] for i in sorted_keys]
        return pd.DataFrame(data_list).round(2)

    # return DataFrame
    def get_local_data(self, code: str, end_time: str, days: int):
        local_data = self.ContextInfo.get_local_data(stock_code=code, end_time=end_time, period='1d', divid_type='front_ratio', count=days)
        return self.__convert_local_data_to_dataframe(local_data)

    # return DataFrame
    def get_local_data_from_start(self, code: str, start_time: str, end_time: str):
        local_data = self.ContextInfo.get_local_data(stock_code=code, start_time=start_time, end_time=end_time, period='1d', divid_type='front_ratio')
        return self.__convert_local_data_to_dataframe(local_data)

    def do_back_test(self) -> bool:
        return self.ContextInfo.do_back_test

    def is_last_bar(self) -> bool:
        return self.ContextInfo.is_last_bar()

    def get_price(self, code: str) -> float:
        if self.do_back_test():
            return self.ContextInfo.get_market_data(["close"], stock_code=[code])
        else:
            return self.ContextInfo.get_full_tick(stock_code=[code])[code]["lastPrice"]

    def get_field(self, code: str, field: str, open_time: str) -> float:
        # get today field value from market open, field can be open,high,low,volume,amount
        if self.do_back_test():
            df = self.ContextInfo.get_market_data([field], stock_code=[code], start_time=open_time, skip_paused=False, period="1m", dividend_type='front_ratio')
            if field == "volume" or field == "amount":
                return np.sum(df[field])
            elif field == "high":
                return np.max(df[field])
            elif field == "low":
                return np.min(df[field])
            elif field == "open":
                return self.get_market_data([field], code, 1).iloc[0][field]
        else:
            return self.ContextInfo.get_full_tick(stock_code=[code])[code][field]

    def get_stock_capital(self, code: str) -> float:
        names = code.split(".")
        return self.ContextInfo.get_financial_data('CAPITALSTRUCTURE', 'circulating_capital', names[1], names[0], self.ContextInfo.barpos)

    def get_capital(self) -> float:
        return self.ContextInfo.capital


class Bar:
    def __init__(self, container: Container) -> None:
        self.container = container

    def get_timestamp(self, ctx: Context) -> str:
        return self.container.timetag_to_datetime(ctx.get_bar_timetag(), "%Y-%m-%d %H:%M:%S")

    def get_bar_datetime(self, ctx: Context) -> datetime:
        pattern = "%Y-%m-%d %H:%M:%S"
        time = self.container.timetag_to_datetime(ctx.get_bar_timetag(), pattern)
        return datetime.strptime(time, pattern)

    def get_bar_date(self, ctx: Context) -> datetime:
        pattern = "%Y-%m-%d"
        time = self.container.timetag_to_datetime(ctx.get_bar_timetag(), pattern)
        return datetime.strptime(time, pattern)

    def get_bar_open_time(self, ctx: Context) -> datetime:
        return self.get_bar_date(ctx).replace(hour=9, minute=30, second=0)

    def get_bar_open_str_time(self, ctx: Context) -> str:
        pattern = "%Y%m%d%H%M%S"
        start = self.get_bar_open_time(ctx)
        return start.strftime(pattern)

    def get_open_seconds(self, ctx: Context) -> int:
        bar_time = self.get_bar_time(ctx)
        if bar_time < "09:30:00" or bar_time > "15:00:00":
            return 0

        current = self.get_bar_datetime(ctx)
        open = self.get_bar_open_time(ctx)
        seconds = int((current - open).total_seconds())
        bar_time = self.get_bar_time(ctx)
        if bar_time >= "13:00:00":
            return int(seconds - 90 * 60)
        else:
            return seconds

    def get_bar_time(self, ctx: Context) -> str:
        return self.container.timetag_to_datetime(ctx.get_bar_timetag(), "%H:%M:%S")

    def is_load_bar(self, ctx: Context) -> bool:
        bar_time = self.get_bar_time(ctx)
        return bar_time >= "06:00:00" and bar_time < "14:55:00"

    def is_trade_bar(self, ctx: Context) -> bool:
        bar_time = self.get_bar_time(ctx)
        return bar_time >= "09:30:00" and bar_time < "14:55:00"

    def is_early_bar(self, ctx: Context) -> bool:
        bar_time = self.get_bar_time(ctx)
        return bar_time >= "09:30:00" and bar_time <= "10:00:00"

    def is_close_bar(self, ctx: Context) -> bool:
        bar_time = self.get_bar_time(ctx)
        return bar_time == "14:55:00"

    def is_adjust_bar(self, ctx: Context, time: str) -> bool:
        bar_time = self.get_bar_time(ctx)
        return bar_time == time

    def is_history_bar(self, ctx: Context) -> bool:
        return not ctx.is_last_bar() and not ctx.do_back_test()


class Log:

    def __init__(self, container: Container) -> None:
        self.bar = Bar(container)

    def __print_msg(self, msg: str, ctx: Context):
        if ctx:
            print("")
            print(f"{self.bar.get_timestamp(ctx)}: {msg}")
        else:
            print(msg)

    # ctx: default value is None, if pass value, it will print bar timestamp and it is useful for back testing.
    def log_debug(self, msg: str, ctx: Context = None) -> None:
        if Setting.log_level <= 0:
            self.__print_msg(msg, ctx)

    def log_info(self, msg: str, ctx: Context = None) -> None:
        if Setting.log_level <= 1:
            self.__print_msg(msg, ctx)

    def log_warn(self, msg: str, ctx: Context = None) -> None:
        if Setting.log_level <= 2:
            self.__print_msg(msg, ctx)

    def log_error(self, msg: str, ctx: Context = None) -> None:
        if Setting.log_level <= 3:
            self.__print_msg(msg, ctx)
