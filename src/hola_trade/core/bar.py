from hola_trade.core.ctx import Context
from hola_trade.core.container import Container


class Bar:
    def __init__(self, container: Container):
        self.container = container

    def get_timestamp(self, ctx: Context) -> str:
        return self.container.timetag_to_datetime(ctx.get_bar_timetag(), "%Y-%m-%d %H:%M:%S")

    def get_bar_time(self, ctx: Context) -> str:
        return self.container.timetag_to_datetime(ctx.get_bar_timetag(), "%H:%M:%S")

    def is_trade_bar(self, ctx: Context) -> bool:
        bar_time = self.get_bar_time(ctx)
        return bar_time >= "09:30:00" and bar_time < "14:55:00"

    def is_close_bar(self, ctx: Context) -> bool:
        bar_time = self.get_bar_time(ctx)
        return bar_time == "14:55:00"

    def is_adjust_bar(self, ctx: Context, time: str) -> bool:
        bar_time = self.get_bar_time(ctx)
        return bar_time == time

    def is_history_bar(self, ctx: Context) -> bool:
        return not ctx.is_last_bar() and not ctx.do_back_test()
