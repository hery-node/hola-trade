from typing import List, Optional
from hola_trade.core.ctx import Context, Container, Log


class Account:
    def __init__(self, id: str, cash: float, total_assets: float) -> None:
        self.id = id
        self.cash = round(cash, 2)
        self.stock_value = round(total_assets - cash, 2)
        self.total_assets = round(total_assets, 2)


class Holding:
    def __init__(self, code: str, open_date: str, open_price: float, price: float, available: int, volume: int, value: float, profit: float,  today: bool) -> None:
        self.code = code
        self.open_date = open_date
        self.open_price = round(open_price, 2)
        self.price = round(price, 2)
        self.available = int(available)
        self.volume = int(volume)
        self.value = round(value, 2)
        self.profit = round(profit, 2)
        self.profit_rate = 0 if value == 0 else round(profit * 100 / value, 2)
        self.today = today


class User:
    def __init__(self, id: str, type: str, container: Container) -> None:
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
    def get_instance(cls, id: str, container: Container):
        return cls(id, "STOCK", container)

    def get_positions(self):
        return self.container.get_trade_detail_data(self.id, self.type, "POSITION")

    def get_holdings(self) -> List[Holding]:
        return [Holding(
            self.__get_stock_code(obj),
            obj.m_strOpenDate,
            obj.m_dOpenPrice,
            obj.m_dLastPrice,
            obj.m_nCanUseVolume,
            obj.m_nVolume,
            obj.m_dMarketValue,
            obj.m_dFloatProfit,
            obj.m_bIsToday
        ) for obj in self.get_positions()]

    def get_holding(self, code: str) -> Optional[Holding]:
        holdings = [holding for holding in self.get_holdings() if holding.code == code]
        if len(holdings) == 1:
            return holdings[0]
        else:
            return None

    def get_holding_codes(self) -> List[str]:
        holdings = self.get_holdings()
        return [holding.code for holding in holdings]

    def get_available_holding_codes(self) -> List[str]:
        holdings = self.get_holdings()
        return [holding.code for holding in holdings if holding.available > 0]

    def get_account(self) -> Account:
        account = self.__get_stock_account()
        return Account(self.id, account.m_dAvailable, account.m_dBalance)

    def get_profit(self, start_assets: float) -> float:
        account = self.get_account()
        return round((account.total_assets - start_assets) * 100 / start_assets, 2)

    def order_by_value(self, ctx: Context, code: str, cash: float, price: float = 0) -> None:
        if cash:
            if price:
                self.log.log_info(ctx, f" order_by_cash: code:{code} at price:{price} with cash:{cash}")
                self.container.order_value(code, cash, 'FIX', price, ctx.ContextInfo, self.id)
            else:
                self.log.log_info(ctx, f"order_by_cash: code:{code} with cash:{cash} at latest price")
                self.container.order_value(code, cash, ctx.ContextInfo, self.id)

    def order_by_shares(self, ctx: Context, code: str, share: int, price: float = 0) -> None:
        if share:
            if price:
                self.log.log_info(ctx, f"order_by_shares: code:{code} at price:{price} with share:{share}")
                self.container.order_shares(code, share, 'FIX', price, ctx.ContextInfo, self.id)
            else:
                self.log.log_info(ctx, f"order_by_shares: code:{code} with share:{share} at latest price")
                self.container.order_shares(code, share, ctx.ContextInfo, self.id)
