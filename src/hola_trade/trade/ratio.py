from typing import Tuple
from abc import ABC, abstractmethod
from hola_trade.trade.stock import Stock
from hola_trade.trade.account import User
from hola_trade.core.ctx import Context, Container, Log


class Ratio:
    def __init__(self, num: int, ratio: float) -> None:
        if ratio < 0 or ratio > 1:
            raise ValueError(f"ratio should between 0~1:{ratio}")
        if num < 0:
            raise ValueError(f"num should be positive:{num}")
        self.num = num
        self.ratio = ratio

    def __str__(self):
        return f'num is {self.num} and ratio is {self.ratio}'


class RatioRule(ABC):
    # holding_ratio: ratio: 单只股票占最大持仓的比例,而不是总仓位的比例, num:最大持股数量。 batches:分几次建仓。
    def __init__(self, user: User, container: Container, holding_ratio: Ratio, batches: int):
        if batches <= 0:
            raise ValueError(f"batches should bigger than 0:{batches}")

        self.log = Log(container)
        self.user = user
        self.holding_ratio = holding_ratio
        self.batches = batches
        self.max_ratio_cache = -1

    # reset cached value
    def reset(self) -> None:
        self.max_ratio_cache = -1

    def get_adjust_ratio(self, ctx: Context) -> Tuple[float, float]:
        account = self.user.get_account()
        # cache value, for adjust, use latest value so get again
        self.max_ratio_cache = self.get_max_ratio(ctx)
        stock_ratio = account.stock_ratio
        self.log.log_debug(f"max ratio is {self.max_ratio_cache} and stock ratio is {stock_ratio}", ctx)
        if stock_ratio <= self.max_ratio_cache:
            return round(self.max_ratio_cache, 2), 0

        ratio = (stock_ratio - self.max_ratio_cache) / stock_ratio
        return round(self.max_ratio_cache, 2), round(ratio, 2)

    def get_money(self, ctx: Context, code: str) -> float:
        account = self.user.get_account()
        max_ratio = self.max_ratio_cache if self.max_ratio_cache >= 0 else self.get_max_ratio(ctx)
        # cache value
        self.max_ratio_cache = max_ratio
        self.log.log_debug(f"max ratio is {max_ratio}", ctx)

        max_money = account.total_assets * max_ratio - account.stock_value
        if max_money <= 0:
            self.log.log_info("The holding total value is more than max ratio control, so no money can be used.", ctx)
            return 0

        holding_money = account.total_assets * max_ratio * self.holding_ratio.ratio
        batch_money = holding_money / self.batches

        holding = self.user.get_holding(code)
        if holding:
            holding_left_money = holding_money - holding.value
            if holding_left_money > 0:
                money = round(min([batch_money, holding_left_money, account.cash, max_money]), 2)
                return 0 if money < holding.price * 100 else money
            else:
                self.log.log_info("The holding value has reached holding ratio, so no money can be used.", ctx)
                return 0
        else:
            if len(self.user.get_holdings()) < self.holding_ratio.num:
                return round(min([batch_money, account.cash, max_money]), 2)
            else:
                self.log.log_info(f"The holding number has reached max_holdings:{self.holding_ratio.num}, so no money can be used.", ctx)
                return 0

    @abstractmethod
    def get_max_ratio(self, ctx: Context) -> float:
        # write your policy code here
        pass


class StaticRatioRule(RatioRule):
    def __init__(self, user: User, container: Container, holding_ratio: Ratio, batches: int, max_ratio: float):
        super().__init__(user, container, holding_ratio, batches)
        self.max_ratio = Ratio(0, max_ratio)

    def get_max_ratio(self, ctx: Context) -> float:
        return self.max_ratio.ratio


class SimpleTrendRatioRule(RatioRule):
    def __init__(self, user: User, container: Container, holding_ratio: Ratio, batches: int, main_code: str, short_ratio: Ratio, mid_ratio: Ratio, long_ratio: Ratio, no_ratio: float):
        super().__init__(user, container, holding_ratio, batches)

        self.main_stock = Stock(main_code)
        if not (short_ratio.num <= mid_ratio.num and mid_ratio.num <= long_ratio.num):
            raise ValueError(f"wrong setting: short:{short_ratio.num},mid:{mid_ratio.num},long:{long_ratio.num}")

        if not (short_ratio.ratio <= mid_ratio.ratio and mid_ratio.ratio <= long_ratio.ratio):
            raise ValueError(f"wrong setting: short ratio:{short_ratio.ratio},mid ratio:{mid_ratio.ratio},long ratio:{long_ratio.ratio}")

        self.short_ratio = short_ratio
        self.mid_ratio = mid_ratio
        self.long_ratio = long_ratio
        self.no_ratio = no_ratio

    def get_max_ratio(self, ctx: Context) -> float:
        current_price = self.main_stock.get_price(ctx)
        short_price = self.main_stock.get_avg_price(ctx, self.short_ratio.num)
        mid_price = self.main_stock.get_avg_price(ctx, self.mid_ratio.num)
        long_price = self.main_stock.get_avg_price(ctx, self.long_ratio.num)
        prices = [short_price, mid_price, long_price]
        total = len([price for price in prices if price < current_price])
        self.log.log_debug(f"total:{total}, current:{current_price}, short:{short_price},mid:{mid_price},long:{long_price}", ctx)
        if total == 3:
            return self.long_ratio.ratio
        elif total == 2:
            return self.mid_ratio.ratio
        elif total == 1:
            return self.short_ratio.ratio
        else:
            return self.no_ratio


class TrendRatioRule(RatioRule):
    def __init__(self, user: User, container: Container, holding_ratio: Ratio, batches: int, main_code: str, short_days: float, mid_days: float, long_days: float):
        super().__init__(user, container, holding_ratio, batches)

        self.main_stock = Stock(main_code)
        if not (short_days < mid_days and mid_days < long_days):
            raise ValueError(f"wrong setting: short:{short_days},mid:{mid_days},long:{long_days}")

        self.short_days = short_days
        self.mid_days = mid_days
        self.long_days = long_days

    def get_max_ratio(self, ctx: Context) -> float:
        current_price = self.main_stock.get_price(ctx)
        short_price = self.main_stock.get_avg_price(ctx, self.short_days)
        mid_price = self.main_stock.get_avg_price(ctx, self.mid_days)
        long_price = self.main_stock.get_avg_price(ctx, self.long_days)
        prices = [short_price, mid_price, long_price]
        total = len([price for price in prices if price < current_price])
        self.log.log_debug(f"total:{total}, current:{current_price}, short:{short_price},mid:{mid_price},long:{long_price}", ctx)
        weight = 0
        if short_price >= mid_price and mid_price >= long_price:
            weight = 3
        elif short_price >= long_price and long_price >= mid_price:
            weight = 2
        elif mid_price >= short_price and short_price >= long_price:
            weight = 2
        elif mid_price >= long_price and long_price >= short_price:
            weight = 1
        elif long_price >= short_price and short_price >= mid_price:
            weight = 1
        elif long_price >= mid_price and mid_price >= short_price:
            weight = 0

        ratio = round(0.1 * ((weight+total) if weight == 0 else weight * total), 2)
        self.log.log_debug(f"calculated ratio is {ratio}", ctx)
        return ratio
