from ctx import Ctx
from account import Account
from holding import Holding
from ctx_info import ContextInfo


class User:
    def __init__(self, id: str, type: str, ctx: Ctx):
        self.id = id
        self.type = type
        self.ctx = ctx
        self.log = ctx.log

    def __get_stock_account(self):
        accounts = self.ctx.get_trade_detail_data(self.id, self.type, "ACCOUNT")
        if len(accounts) != 1:
            raise ValueError("there is no valid account or more than one account")
        return accounts[0]

    def __get_stock_code(self, obj) -> str:
        return obj.m_strInstrumentID + "." + obj.m_strExchangeID

    @classmethod
    def get_trade_account(cls, id: str, ctx: Ctx):
        return cls(id, "STOCK", ctx)

    def get_positions(self):
        return self.ctx.get_trade_detail_data(self.id, self.type, "POSITION")

    def get_holdings(self) -> list[Holding]:
        return [Holding(self.__get_stock_code(obj), obj.m_dSettlementPrice, obj.m_nCanUseVolume, obj.m_nVolume, obj.m_dMarketValue) for obj in self.get_positions()]

    def get_account(self) -> Account:
        account = self.__get_stock_account()
        return Account(self.id, account.m_dAvailable, account.m_dStockValue, account.m_dBalance)

    def get_profit(self, start_assets) -> float:
        account = self.get_account()
        profit = (account.total_assets - start_assets) * 100 / start_assets
        return round(profit, 2)

    def get_share(self, money: float, price: float) -> int:
        return int((money // (price * 100)) * 100)

    def order_by_value(self, ctx_info: ContextInfo, code: str, cash: float, price=0):
        if cash:
            if price:
                self.log.log_info(ctx_info, f" order_by_cash: code:{code} at price:{price} with cash:{cash}")
                self.ctx.order_value(code, cash, 'FIX', price, ctx_info.ctx_info, self.id)
            else:
                self.log.log_info(ctx_info, f"order_by_cash: code:{code} with cash:{cash} at latest price")
                self.ctx.order_value(code, cash, ctx_info.ctx_info, self.id)

    def order_by_shares(self, ctx_info: ContextInfo, code: str, share: int, price=0):
        if share:
            if price:
                self.log.log_info(ctx_info, f"order_by_shares: code:{code} at price:{price} with share:{share}")
                self.ctx.order_shares(code, share, 'FIX', price, ctx_info.ctx_info, self.id)
            else:
                self.log.log_info(ctx_info, f"order_by_shares: code:{code} with share:{share} at latest price")
                self.ctx.order_shares(code, share, ctx_info.ctx_info, self.id)
