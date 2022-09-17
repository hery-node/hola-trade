from typing import List
from datetime import datetime


class Container:
    def __init__(self, timetag_to_datetime, get_trade_detail_data, order_value, order_shares) -> None:
        self.timetag_to_datetime = timetag_to_datetime
        self.get_trade_detail_data = get_trade_detail_data
        self.order_value = order_value
        self.order_shares = order_shares


class Context:
    def __init__(self, ContextInfo) -> None:
        self.ContextInfo = ContextInfo

    def get_bar_timetag(self) -> int:
        return self.ContextInfo.get_bar_timetag(self.ContextInfo.barpos)

    def get_stock_list_in_sector(self, sector: str) -> List[str]:
        return self.ContextInfo.get_stock_list_in_sector(sector)

    # return DataFrame
    def get_market_data(self, fields: List[str], code: str, days: int):
        return self.ContextInfo.get_market_data(fields, stock_code=[code], skip_paused=False, period="1d", dividend_type='front_ratio', count=days)

    def do_back_test(self) -> bool:
        return self.ContextInfo.do_back_test

    def is_last_bar(self) -> bool:
        return self.ContextInfo.is_last_bar()

    def get_price(self, code: str) -> float:
        if self.do_back_test():
            return self.ContextInfo.get_market_data(["close"], stock_code=[code])
        else:
            return self.ContextInfo.get_full_tick(stock_code=[code])[code]["lastPrice"]

    def get_amount(self, code: str) -> float:
        if self.do_back_test():
            return self.ContextInfo.get_market_data(["amount"], stock_code=[code])
        else:
            return self.ContextInfo.get_full_tick(stock_code=[code])[code]["amount"]

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

    def get_open_seconds(self, ctx: Context) -> int:
        if not self.is_trade_bar(ctx):
            return 0

        current = self.get_bar_datetime(ctx)
        open = self.get_bar_date(ctx).replace(hour=9, minute=30, second=0)
        seconds = int((current - open).total_seconds())
        bar_time = self.get_bar_time(ctx)
        if bar_time >= "13:00:00":
            return seconds - 90 * 60
        else:
            return seconds

    def get_bar_time(self, ctx: Context) -> str:
        return self.container.timetag_to_datetime(ctx.get_bar_timetag(), "%H:%M:%S")

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
    log_level = 0

    def __init__(self, container: Container) -> None:
        self.bar = Bar(container)

    def log_debug(self, ctx: Context, msg: str) -> None:
        if self.log_level >= 0:
            print(f"{self.bar.get_timestamp(ctx)}: {msg}")

    def log_info(self, ctx: Context, msg: str) -> None:
        if self.log_level >= 1:
            print(f"{self.bar.get_timestamp(ctx)}: {msg}")

    def log_warn(self, ctx: Context, msg: str) -> None:
        if self.log_level >= 2:
            print(f"{self.bar.get_timestamp(ctx)}: {msg}")

    def log_error(self, ctx: Context, msg: str) -> None:
        if self.log_level >= 3:
            print(f"{self.bar.get_timestamp(ctx)}: {msg}")
