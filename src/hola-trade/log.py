from bar import Bar
from ctx import Ctx
from ctx_info import ContextInfo


class Log:
    def __init__(self, level: int, ctx: Ctx):
        self.level = level
        self.bar = Bar(ctx)

    def log_debug(self, ctx_info: ContextInfo, msg: str):
        if self.level >= 0:
            print(f"{self.bar.get_timestamp(ctx_info)}: {msg}")

    def log_info(self, ctx_info: ContextInfo, msg: str):
        if self.level >= 1:
            print(f"{self.bar.get_timestamp(ctx_info)}: {msg}")

    def log_warn(self, ctx_info: ContextInfo, msg: str):
        if self.level >= 2:
            print(f"{self.bar.get_timestamp(ctx_info)}: {msg}")

    def log_error(self, ctx_info: ContextInfo, msg: str):
        if self.level >= 3:
            print(f"{self.bar.get_timestamp(ctx_info)}: {msg}")
