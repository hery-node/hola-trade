from bar import Bar
from ctx import Ctx


class Policy:
    def __init__(self, name: str, ctx: Ctx):
        self.name = name
        self.ctx = ctx
        self.bar = Bar(ctx)

    def init(self, ContextInfo):
        pass

    def handlebar(self, ContextInfo):
        # in real trade, pass history bars
        if not ContextInfo.is_last_bar() and not ContextInfo.do_back_test:
            return

        if not self.bar.is_trade_bar(ContextInfo):
            return
