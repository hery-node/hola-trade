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
        # use to cache max_ratio during load to avoid duplicate compute
        self.max_ratio_cache = 0
        # if adjusted, then no opening or add
        self.adjusted = False
        self.loaded = False
        self.cleaned = False
        self.enabled = True

    def load(self, ctx: Context) -> None:
        pass

    def clean(self, ctx: Context) -> None:
        pass

    # simpel check to avoid complex compute and boost performance
    def can_open_target(self, ctx: Context) -> bool:
        account = self.user.get_account()
        holding_limit = self.ratio_rule.holding_ratio.num
        holding_num = len(self.user.get_holding_codes())
        result = account.cash > 0 and holding_num < holding_limit and account.stock_ratio < self.max_ratio_cache
        self.log.log_debug(f"can_open_target:{result}, holding_limit:{holding_limit}, holding num is {holding_num}, max_ratio is {self.max_ratio_cache}, account status is {account}", ctx)
        return result

    def handle_bar(self, ctx: Context) -> None:
        if self.bar.is_history_bar(ctx):
            return

        if (not self.loaded) and self.bar.is_load_bar(ctx):
            self.log.log_debug("begin loading", ctx)
            self.max_ratio_cache = self.ratio_rule.get_max_ratio(ctx)

            if self.can_open_target(ctx):
                codes = ctx.get_stock_list_in_sector(self.sector)
                targets = self.policy_conditions.select_condition.filter(self.bar, ctx, self.user, codes)
                holding_codes = self.user.get_holding_codes()
                self.codes = [target.code for target in targets if target.code not in holding_codes]
            else:
                self.codes = []

            self.load(ctx)
            self.cleaned = False
            self.loaded = True
            self.log.log_debug(f"complete loading and target number is {len(self.codes)}", ctx)

        if self.enabled and self.loaded and self.bar.is_trade_bar(ctx):
            available_holding_codes = self.user.get_available_holding_codes()
            available_holding_num = len(available_holding_codes)

            # first check to boost performance
            if len(self.codes) > 0 and (not self.adjusted) and self.can_open_target(ctx):
                buy_targets = self.policy_conditions.buy_condition.filter(self.bar, ctx, self.user, self.codes)
                if buy_targets and len(buy_targets) > 0:
                    for target in buy_targets:
                        # 开仓受仓位的控制，所以从仓位控制中获得资金
                        money = self.ratio_rule.get_money(ctx, target.code)
                        if money > 0:
                            self.log.log_debug(f"{target.code} meets the buy condition and buy it", ctx)
                            self.user.buy_by_value(ctx, target.code, money, target.price, self.name)

                if available_holding_num > 0:
                    add_targets = self.policy_conditions.add_condition.filter(self.bar, ctx, self.user, available_holding_codes)
                    if add_targets and len(add_targets) > 0:
                        for target in add_targets:
                            # 加仓受仓位的控制，所以从仓位控制中获得资金
                            money = self.ratio_rule.get_money(ctx, target.code)
                            if money > 0:
                                self.log.log_debug(f"{target.code} meets the add condition and add it", ctx)
                                self.user.buy_by_value(ctx, target.code, money, target.price, self.name)

            if available_holding_num > 0:
                sell_targets = self.policy_conditions.sell_condition.filter(self.bar, ctx, self.user, available_holding_codes)
                if sell_targets and len(sell_targets) > 0:
                    for target in sell_targets:
                        # 减仓不受仓位的控制，所以从条件中获得卖出金额
                        self.log.log_debug(f"{target.code} meets the sell condition and sell it", ctx)
                        self.user.sell_by_value(ctx, target.code, target.value, target.price, self.name)

                clear_targets = self.policy_conditions.clear_condition.filter(self.bar, ctx, self.user, available_holding_codes)
                if clear_targets and len(clear_targets) > 0:
                    for target in clear_targets:
                        # 清仓
                        self.log.log_debug(f"{target.code} meets the clear condition and clear it", ctx)
                        self.user.clear_holding(ctx, target.code, target.price)

            if available_holding_num > 0 and self.bar.is_adjust_bar(ctx, self.adjust_time):
                max_ratio, ratio = self.ratio_rule.get_adjust_ratio(ctx)
                if ratio > 0:
                    self.adjusted = True
                    holdings = self.user.get_holdings()
                    for holding in holdings:
                        # 按照比例减仓
                        cash = min([holding.available * holding.price, holding.value * ratio])
                        if cash > 0:
                            self.log.log_debug(f"{holding.code} meets the adjust condition and adjust it", ctx)
                            self.user.sell_by_value(ctx, holding.code, cash, 0, self.name)
                else:
                    if max_ratio > self.max_ratio_cache:
                        # 由于市场变化,max ratio变大了,可以加仓了,所以需要重新load
                        self.loaded = False
                        self.max_ratio_cache = max_ratio

        if (not self.cleaned) and self.bar.is_close_bar(ctx):
            self.log.log_debug("begin cleaning", ctx)
            self.ratio_rule.reset()
            self.clean(ctx)
            self.cleaned = True
            self.loaded = False
            self.adjusted = False
            self.log.log_debug("complete cleaning", ctx)

            if ctx.do_back_test():
                profit = self.user.get_profit(ctx.get_capital())
                self.log.log_info(f"total profit: {profit}%", ctx)
