from ctx import Ctx
from ctx_info import ContextInfo


class Bar:
    def __init__(self, ctx: Ctx):
        self.ctx = ctx

    def get_timestamp(self, ctx_info: ContextInfo) -> str:
        return self.ctx.timetag_to_datetime(ctx_info.get_bar_timetag(), "%Y-%m-%d %H:%M:%S")

    def get_bar_time(self, ctx_info: ContextInfo) -> str:
        return self.ctx.timetag_to_datetime(ctx_info.get_bar_timetag(), "%H:%M:%S")

    def is_end_bar(self, ctx_info: ContextInfo) -> bool:
        bar_time = self.get_bar_time(ctx_info)
        return bar_time >= "14:55:00" and bar_time < "15:00:00"

    def is_trade_bar(self, ctx_info: ContextInfo) -> bool:
        bar_time = self.get_bar_time(ctx_info)
        return bar_time >= "09:30:00" and bar_time < "15:00:00"

    def is_close_bar(self, ctx_info: ContextInfo) -> bool:
        bar_time = self.get_bar_time(ctx_info)
        return bar_time == "15:00:00"
