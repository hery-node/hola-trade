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

    @abstractmethod
    def load(self):
        # load codes or other loading
        pass

    @abstractmethod
    def clean(self):
        # do some cleaning
        pass

    @abstractmethod
    def process_bar(self, ctx: Context):
        # write your policy code here
        pass

    def init_setting(self, policy_ratio: float, max_ratio: float, policy_holdings: int, max_holdings: int):
        if policy_ratio <= 0 or policy_ratio > 1:
            raise ValueError(f"policy_ratio should between 0~1:{policy_ratio}")

        if max_ratio <= 0 or max_ratio > 1:
            raise ValueError(f"max_ratio should between 0~1:{max_ratio}")

        if policy_holdings > 0 and max_holdings > 0 and policy_holdings > max_holdings:
            raise ValueError(f"policy_holdings:{policy_holdings} should less than max_holdings:{max_holdings}")

        account = self.user.get_account()
        stock_ratio = account.stock_value / account.total_assets
        if stock_ratio >= max_ratio:
            self.enabled = False
            return

        account_holdings = len(self.user.get_holdings())
        if max_holdings > 0 and max_holdings < account_holdings:
            self.enabled = False
            return

        max_cash = account.total_assets * max_ratio - account.stock_value
        policy_cash = account.total_assets * policy_ratio
        self.cash = min([max_cash, policy_cash, account.cash])
        self.holdings_num = -1
        if policy_holdings > 0:
            if max_holdings > 0:
                self.holdings_num = min([policy_holdings, max_holdings - account_holdings])
            else:
                self.holdings_num = policy_holdings
        else:
            if max_holdings > 0:
                self.holdings_num = max_holdings - account_holdings

        self.enabled = True

    def handle_bar(self, ctx: Context):
        if (not self.enabled) or (self.bar.is_history_bar(ctx)):
            return

        if (not self.loaded) and self.bar.is_trade_bar(ctx):
            self.load()
            self.cleaned = False
            self.loaded = True

        if (not self.cleaned) and self.bar.is_close_bar(ctx):
            self.clean()

            if ctx.do_back_test():
                profit = self.user.get_profit(ctx.get_capital())
                self.log.log_info(ctx, f"total profit: {profit}%")

            self.cleaned = True
            self.loaded = False

        self.process_bar(ctx)
