from typing import List
from hola_trade.trade.account import User
from hola_trade.core.ctx import Context, Bar, Log, Container
from hola_trade.trade.ratio import RatioRule
from hola_trade.trade.condition import PolicyConditions
from hola_trade.trade.stock import Stock

MONEY = 20000
LOW_DAYS = 3
MID_DAYS = 8
SELL_RATE = 5
BUY_RATE = -4


class MyPolicy:
    def __init__(self, name: str, sector: str, user: User,  container: Container):
        self.name = name
        self.sector = sector
        self.user = user
        self.container = container
        self.bar = Bar(container)
        self.log = Log(container)

    def handle_bar(self, ctx: Context) -> None:
        if self.bar.is_history_bar(ctx):
            return

        account = self.user.get_account()
        codes = self.user.get_available_holding_codes()

        if self.bar.is_trade_bar(ctx) and codes and len(codes) > 0:
            # low buy
            if account.cash > MONEY:
                for target in codes:
                    stock = Stock(target)
                    short_price = stock.get_avg_price(ctx, LOW_DAYS)
                    mid_price = stock.get_avg_price(ctx, MID_DAYS)
                    # up trends
                    if short_price > mid_price * 1.01:
                        pass

            # high sell
