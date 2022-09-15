from abc import ABC, abstractmethod
from hola_trade.core.bar import Bar
from hola_trade.core.log import Log
from hola_trade.trade.user import User
from hola_trade.core.ctx import Context
from hola_trade.core.container import Container


class Policy(ABC):
    def __init__(self, name: str, user: User,  container: Container):
        self.name = name
        self.user = user
        self.container = container
        self.bar = Bar(container)
        self.log = Log(container)
        self.codes = []
        self.loaded = False
        self.cleaned = False
        self.enabled = False

    def load_codes(self, ctx: Context) -> list[str]:
        return []

    def load(self, ctx: Context):
        pass

    def clean(self, ctx: Context):
        self.codes = []
        pass

    @abstractmethod
    def process_bar(self, ctx: Context):
        # write your policy code here
        pass

    def init_setting(self, holding_ratio: float,  max_ratio: float, max_holdings: int):
        if holding_ratio <= 0 or holding_ratio > 1:
            raise ValueError(f"holding_ratio should between 0~1:{holding_ratio}")

        if max_ratio <= 0 or max_ratio > 1:
            raise ValueError(f"max_ratio should between 0~1:{max_ratio}")

        self.holding_ratio = holding_ratio
        self.max_ratio = max_ratio
        self.max_holdings = max_holdings
        self.enabled = True

    def get_money(self, code: str) -> float:
        account = self.user.get_account()
        max_money = account.total_assets * self.max_ratio - account.stock_value
        if max_money <= 0:
            self.log.log_warn("The holding total value is more than max ratio control, so no money can be used.")
            return 0

        holding = self.user.get_holding(code)
        if holding:
            holding_money = account.total_assets * self.holding_ratio - holding.value
            if holding_money > 0:
                return min([holding_money, account.cash, max_money])
            else:
                self.log.log_warn("The holding value has reached holding ratio, so no money can be used.")
                return 0
        else:
            if len(self.user.get_holdings()) < self.max_holdings:
                return min([account.total_assets * self.holding_ratio, account.cash, max_money])
            else:
                self.log.log_warn("The holding number has reached max_holdings, so no money can be used.")
                return 0

    def handle_bar(self, ctx: Context):
        if (not self.enabled) or (self.bar.is_history_bar(ctx)):
            return

        if (not self.loaded) and self.bar.is_trade_bar(ctx):
            self.codes = self.load_codes(ctx)
            self.load(ctx)
            self.cleaned = False
            self.loaded = True

        if (not self.cleaned) and self.bar.is_close_bar(ctx):
            self.clean(ctx)

            if ctx.do_back_test():
                profit = self.user.get_profit(ctx.get_capital())
                self.log.log_info(ctx, f"total profit: {profit}%")

            self.cleaned = True
            self.loaded = False

        self.process_bar(ctx)
