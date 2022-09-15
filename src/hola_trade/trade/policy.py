from hola_trade.core.bar import Bar
from hola_trade.core.log import Log
from hola_trade.trade.user import User
from hola_trade.core.ctx import Context
from hola_trade.core.container import Container
from hola_trade.trade.ratio import RatioRule
from hola_trade.trade.condition import PolicyConditions


class Policy:
    def __init__(self, name: str, user: User,  container: Container, ratio_rule: RatioRule, policy_conditions: PolicyConditions):
        self.name = name
        self.user = user
        self.container = container
        self.bar = Bar(container)
        self.log = Log(container)
        self.codes = []
        self.ratio_rule = ratio_rule
        self.policy_conditions = policy_conditions
        self.loaded = False
        self.cleaned = False
        self.enabled = False

    def load(self, ctx: Context):
        pass

    def clean(self, ctx: Context):
        pass

    def handle_bar(self, ctx: Context):
        if (not self.enabled) or (self.bar.is_history_bar(ctx)):
            return

        if (not self.loaded) and self.bar.is_trade_bar(ctx):
            self.codes = self.policy_conditions.select_condition.filter_codes(ctx, ctx.get_all_codes())
            self.load(ctx)
            self.cleaned = False
            self.loaded = True

        if self.bar.is_trade_bar(ctx):
            buy_codes = self.policy_conditions.buy_condition.filter_codes(self.codes)
            for code in buy_codes:
                money = self.ratio_rule.get_money(ctx, code)
                if money > 0:
                    self.user.order_by_value(ctx, code, money)

            sell_codes = self.policy_conditions.sell_condition.filter_codes(self.user.get_holding_codes())
            for code in sell_codes:
                money = self.user.get_holding(code).value / self.ratio_rule.batches
                self.user.order_by_value(ctx, code, money*-1)

            add_codes = self.policy_conditions.add_condition.filter_codes(self.user.get_holding_codes())
            for code in add_codes:
                money = self.ratio_rule.get_money(ctx, code)
                if money > 0:
                    self.user.order_by_value(ctx, code, money)

            clear_codes = self.policy_conditions.clear_condition.filter_codes(self.user.get_holding_codes())
            for code in clear_codes:
                holding = self.user.get_holding(code)
                self.user.order_by_shares(ctx, code, holding.available)

        if (not self.cleaned) and self.bar.is_close_bar(ctx):
            self.clean(ctx)

            if ctx.do_back_test():
                profit = self.user.get_profit(ctx.get_capital())
                self.log.log_info(ctx, f"total profit: {profit}%")

            self.cleaned = True
            self.loaded = False
