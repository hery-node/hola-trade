from bar import Bar
from ctx import Ctx


class Log:
    def __init__(self, level: int, ctx: Ctx):
        self.level = level
        self.bar = Bar(ctx)

    def log_debug(self, ContextInfo, msg):
        if self.level >= 0:
            print(f"{self.bar.get_time_stamp(ContextInfo)}: {msg}")

    def log_info(self, ContextInfo, msg):
        if self.level >= 1:
            print(f"{self.bar.get_time_stamp(ContextInfo)}: {msg}")

    def log_warn(self, ContextInfo, msg):
        if self.level >= 2:
            print(f"{self.bar.get_time_stamp(ContextInfo)}: {msg}")

    def log_error(self, ContextInfo, msg):
        if self.level >= 3:
            print(f"{self.bar.get_time_stamp(ContextInfo)}: {msg}")
