from ctx import Ctx


class Bar:
    def __init__(self, ctx: Ctx):
        self.ctx = ctx

    def get_time_stamp(self, ContextInfo) -> str:
        time_tag = ContextInfo.get_bar_timetag(ContextInfo.barpos)
        return self.ctx.timetag_to_datetime(time_tag, "%Y-%m-%d %H:%M:%S")

    def get_bar_time(self, ContextInfo) -> str:
        time_tag = ContextInfo.get_bar_timetag(ContextInfo.barpos)
        return self.ctx.timetag_to_datetime(time_tag, "%H:%M:%S")

    def is_end_bar(self, ContextInfo) -> bool:
        bar_time = self.get_bar_time(ContextInfo)
        return bar_time >= "14:55:00" and bar_time < "15:00:00"

    def is_trade_bar(self, ContextInfo) -> bool:
        bar_time = self.get_bar_time(ContextInfo)
        return bar_time >= "09:30:00" and bar_time < "15:00:00"

    def is_close_bar(self, ContextInfo) -> bool:
        bar_time = self.get_bar_time(ContextInfo)
        return bar_time == "15:00:00"
