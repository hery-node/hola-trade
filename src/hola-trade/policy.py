from bar import Bar
from ctx import Ctx
from user import User
from ctx_info import ContextInfo


class Policy:
    def __init__(self, name: str, ctx: Ctx, user: User, value_ratio: float):
        self.name = name
        self.ctx = ctx
        self.bar = Bar(ctx)
        self.user = user
        account = user.get_account()
        if value_ratio > 0 and value_ratio <= 1:
            cash = account.total_assets * value_ratio
            self.cash = cash if cash < account.cash else account.cash
        else:
            raise ValueError(f"error value_ratio:{value_ratio}")

    def handlebar(self, ctx_info: ContextInfo):
        # in real trade, pass history bars
        if not ContextInfo.is_last_bar() and not ContextInfo.do_back_test:
            return

        if not self.bar.is_trade_bar(ContextInfo):
            return
