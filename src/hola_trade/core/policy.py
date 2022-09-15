from hola_trade.core.bar import Bar
from hola_trade.trade.account import Account
from hola_trade.trade.user import User
from hola_trade.core.ctx import Context
from hola_trade.core.container import Container


class Policy:
    def __init__(self, name: str, user: User,  container: Container):
        self.name = name
        self.user = user
        self.bar = Bar(container)
        self.container = container
        self.enabled = False

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

    def handlebar(self, ctx: Context):
        if not self.enabled:
            return

        if self.bar.is_history_bar(ctx) or (not self.bar.is_trade_bar(Context)):
            return
