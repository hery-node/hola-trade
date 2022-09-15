from hola_trade.core.bar import Bar
from hola_trade.core.ctx import Context
from hola_trade.core.container import Container


class Log:
    log_level = 0

    def __init__(self, container: Container):
        self.bar = Bar(container)

    def log_debug(self, ctx: Context, msg: str):
        if self.log_level >= 0:
            print(f"{self.bar.get_timestamp(ctx)}: {msg}")

    def log_info(self, ctx: Context, msg: str):
        if self.log_level >= 1:
            print(f"{self.bar.get_timestamp(ctx)}: {msg}")

    def log_warn(self, ctx: Context, msg: str):
        if self.log_level >= 2:
            print(f"{self.bar.get_timestamp(ctx)}: {msg}")

    def log_error(self, ctx: Context, msg: str):
        if self.log_level >= 3:
            print(f"{self.bar.get_timestamp(ctx)}: {msg}")