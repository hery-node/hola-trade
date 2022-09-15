from hola_trade.core.log import Log
from hola_trade.core.ctx import Context
from hola_trade.trade.account import Account
from hola_trade.core.container import Container
from hola_trade.trade.holding import Holding


class User:
    def __init__(self, id: str, type: str, container: Container):
        self.id = id
        self.type = type
        self.container = container
        self.log = Log(container)

    def __get_stock_account(self):
        accounts = self.container.get_trade_detail_data(self.id, self.type, "ACCOUNT")
        if len(accounts) != 1:
            raise ValueError("there is no valid account or more than one account")
        return accounts[0]

    def __get_stock_code(self, obj) -> str:
        return obj.m_strInstrumentID + "." + obj.m_strExchangeID

    @classmethod
    def get_trade_account(cls, id: str, container: Container):
        return cls(id, "STOCK", container)

    def get_positions(self):
        return self.container.get_trade_detail_data(self.id, self.type, "POSITION")

    def get_holdings(self) -> list[Holding]:
        return [Holding(self.__get_stock_code(obj), obj.m_dSettlementPrice, obj.m_nCanUseVolume, obj.m_nVolume, obj.m_dMarketValue) for obj in self.get_positions()]

    def get_account(self) -> Account:
        account = self.__get_stock_account()
        return Account(self.id, account.m_dAvailable, account.m_dStockValue, account.m_dBalance)

    def get_profit(self, start_assets: float) -> float:
        account = self.get_account()
        profit = (account.total_assets - start_assets) * 100 / start_assets
        return round(profit, 2)

    def order_by_value(self, ctx: Context, code: str, cash: float, price=0):
        if cash:
            if price:
                self.log.log_info(ctx, f" order_by_cash: code:{code} at price:{price} with cash:{cash}")
                self.container.order_value(code, cash, 'FIX', price, ctx.ContextInfo, self.id)
            else:
                self.log.log_info(ctx, f"order_by_cash: code:{code} with cash:{cash} at latest price")
                self.container.order_value(code, cash, ctx.ContextInfo, self.id)

    def order_by_shares(self, ctx: Context, code: str, share: int, price=0):
        if share:
            if price:
                self.log.log_info(ctx, f"order_by_shares: code:{code} at price:{price} with share:{share}")
                self.container.order_shares(code, share, 'FIX', price, ctx.ContextInfo, self.id)
            else:
                self.log.log_info(ctx, f"order_by_shares: code:{code} with share:{share} at latest price")
                self.container.order_shares(code, share, ctx.ContextInfo, self.id)
