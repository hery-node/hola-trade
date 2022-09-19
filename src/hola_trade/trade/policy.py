from typing import List
from hola_trade.trade.account import User
from hola_trade.core.ctx import Context, Bar, Log, Container
from hola_trade.trade.ratio import RatioRule
from hola_trade.trade.condition import PolicyConditions


class Policy:
    def __init__(self, name: str, sector: str, user: User,  container: Container, adjust_time: str, ratio_rule: RatioRule, policy_conditions: PolicyConditions):
        self.name = name
        self.sector = sector
        self.user = user
        self.container = container
        self.bar = Bar(container)
        self.log = Log(container)
        self.codes: List[str] = []
        self.adjust_time = adjust_time
        self.ratio_rule = ratio_rule
        self.policy_conditions = policy_conditions
        self.loaded = False
        self.cleaned = False
        self.enabled = True

    def load(self, ctx: Context) -> None:
        pass

    def clean(self, ctx: Context) -> None:
        pass

    def handle_bar(self, ctx: Context) -> None:
        self.log.log_debug("handle_bar", ctx)
        if (not self.enabled) or (self.bar.is_history_bar(ctx)):
            return

        if (not self.loaded) and self.bar.is_trade_bar(ctx):
            self.log.log_debug("begin loading", ctx)
            holding_codes = self.user.get_holding_codes()
            holding_num = self.ratio_rule.holding_ratio.num
            if len(holding_codes) < holding_num:
                codes = ctx.get_stock_list_in_sector(self.sector)
                targets = self.policy_conditions.select_condition.filter(self.bar, ctx, self.user, codes)
                self.codes = [target.code for target in targets]
            else:
                self.codes = []

            self.load(ctx)
            self.cleaned = False
            self.loaded = True
            self.log.log_debug("complete loading", ctx)

        if self.bar.is_trade_bar(ctx):
            self.log.log_debug("handling policy logic", ctx)
            buy_targets = self.policy_conditions.buy_condition.filter(self.bar, ctx, self.user, self.codes)
            for target in buy_targets:
                # 开仓受仓位的控制，所以从仓位控制中获得资金
                money = self.ratio_rule.get_money(ctx, target.code)
                if money > 0:
                    self.log.log_debug(f"{target.code} meets the buy condition and buy it", ctx)
                    self.user.buy_by_value(ctx, target.code, money, 0, self.name)

            holding_codes = self.user.get_available_holding_codes()
            add_targets = self.policy_conditions.add_condition.filter(self.bar, ctx, self.user, holding_codes)
            for target in add_targets:
                # 加仓受仓位的控制，所以从仓位控制中获得资金
                money = self.ratio_rule.get_money(ctx, target.code)
                if money > 0:
                    self.log.log_debug(f"{target.code} meets the add condition and add it", ctx)
                    self.user.buy_by_value(ctx, target.code, money, 0, self.name)

            sell_targets = self.policy_conditions.sell_condition.filter(self.bar, ctx, self.user, holding_codes)
            for target in sell_targets:
                # 减仓不受仓位的控制，所以从条件中获得卖出金额
                self.log.log_debug(f"{target.code} meets the sell condition and sell it", ctx)
                self.user.sell_by_value(ctx, target.code, target.value, 0, self.name)

            clear_targets = self.policy_conditions.clear_condition.filter(self.bar, ctx, self.user, holding_codes)
            for target in clear_targets:
                # 清仓用share来卖出
                self.log.log_debug(f"{target.code} meets the clear condition and clear it", ctx)
                self.user.clear_holding(ctx, target.code)

            if self.bar.is_adjust_bar(ctx, self.adjust_time):
                ratio = self.ratio_rule.get_adjust_ratio(ctx)
                if ratio > 0:
                    holdings = self.user.get_holdings()
                    for holding in holdings:
                        # 按照比例减仓
                        cash = min([holding.available * holding.price, holding.value * ratio])
                        if cash > 0:
                            self.log.log_debug(f"{holding.code} meets the adjust condition and adjust it", ctx)
                            self.user.sell_by_value(ctx, holding.code, cash, 0, self.name)

        if (not self.cleaned) and self.bar.is_close_bar(ctx):
            self.log.log_debug("begin cleaning", ctx)
            self.clean(ctx)
            self.log.log_debug("complete cleaning", ctx)

            if ctx.do_back_test():
                profit = self.user.get_profit(ctx.get_capital())
                self.log.log_info(f"total profit: {profit}%", ctx)

            self.cleaned = True
            self.loaded = False
