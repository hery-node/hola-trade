from typing import List, Optional
from hola_trade.core.ctx import Setting, Context, Container, Log


class Account:
    def __init__(self, id: str, cash: float, total_assets: float) -> None:
        self.id = id
        self.cash = round(cash, 2)
        self.stock_value = round(total_assets - cash, 2)
        self.total_assets = round(total_assets, 2)

    def __str__(self):
        return f'id is {self.id}, cash is {self.cash}, stock_value is {self.stock_value}, total_assets is {self.total_assets}'


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

    def __str__(self):
        return f'code is {self.code}, open_date is {self.open_date}, open_price is {self.open_price}, price is {self.price}, available is {self.available}, volume is {self.volume}, value is {self.value}, profit is {self.profit}, profit_rate is {self.profit_rate}% and today is {self.today}'


class User:
    def __init__(self, id: str, type: str, container: Container) -> None:
        self.id = id
        self.type = type
        self.container = container
        self.log = Log(container)
        self.buy_code = 23 if type == 'STOCK' else 33
        self.sell_code = 24 if type == 'STOCK' else 34
        self.type_order_by_share = 1101
        self.type_order_by_value = 1102
        self.type_order_by_total_ratio = 1113
        self.type_order_by_available_ratio = 1123
        self.price_fixed = 11

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

    # passorder(opType, orderType, accountid, orderCode, prType, modelprice, volume[, strategyName, quickTrade, userOrderId], ContextInfo)
    def __pass_order(self, ctx: Context, op_type: int, order_type: int, code: str, pr_type: int, num: float, price: float = 0, policy: str = ""):
        action = "buy" if op_type == self.buy_code else "sell"
        unit = "share" if order_type == self.type_order_by_share else ("value" if order_type == self.type_order_by_value else ("total ratio" if order_type == self.type_order_by_total_ratio else "available ratio"))
        price_type = "fixed" if pr_type == self.price_fixed else str(pr_type)
        self.log.log_info(f"{action} code:{code} using pr_type:{price_type} at price:{price} with {num} {unit} [{policy}]", ctx)
        self.container.passorder(op_type, order_type, self.id, code, pr_type, price, num, policy, Setting.quick_trade, "", ctx.ContextInfo)

    def buy_by_value(self, ctx: Context, code: str, cash: float, price: float = 0, policy: str = "") -> None:
        pr_type = self.price_fixed if price > 0 else Setting.price_mode
        self.__pass_order(ctx, self.buy_code, self.type_order_by_value, code, pr_type, cash, price, policy)

    def buy_by_share(self, ctx: Context, code: str, share: int, price: float = 0, policy: str = "") -> None:
        pr_type = self.price_fixed if price > 0 else Setting.price_mode
        self.__pass_order(ctx, self.buy_code, self.type_order_by_share, code, pr_type, share, price, policy)

    def buy_by_total_ratio(self, ctx: Context, code: str, ratio: float, price: float = 0, policy: str = "") -> None:
        if ratio <= 0 or ratio > 1:
            raise ValueError(f"ratio should between 0~1")

        pr_type = self.price_fixed if price > 0 else Setting.price_mode
        self.__pass_order(ctx, self.buy_code, self.type_order_by_total_ratio, code, pr_type, ratio, price, policy)

    def buy_by_available_ratio(self, ctx: Context, code: str, ratio: float, price: float = 0, policy: str = "") -> None:
        if ratio <= 0 or ratio > 1:
            raise ValueError(f"ratio should between 0~1")

        pr_type = self.price_fixed if price > 0 else Setting.price_mode
        self.__pass_order(ctx, self.buy_code, self.type_order_by_available_ratio, code, pr_type, ratio, price, policy)

    def sell_by_value(self, ctx: Context, code: str, cash: float, price: float = 0, policy: str = "") -> None:
        pr_type = self.price_fixed if price > 0 else Setting.price_mode
        self.__pass_order(ctx, self.sell_code, self.type_order_by_value, code, pr_type, cash, price, policy)

    def sell_by_share(self, ctx: Context, code: str, share: int, price: float = 0, policy: str = "") -> None:
        pr_type = self.price_fixed if price > 0 else Setting.price_mode
        self.__pass_order(ctx, self.sell_code, self.type_order_by_share, code, pr_type, share, price, policy)

    def sell_by_total_ratio(self, ctx: Context, code: str, ratio: float, price: float = 0, policy: str = "") -> None:
        if ratio <= 0 or ratio > 1:
            raise ValueError(f"ratio should between 0~1")

        pr_type = self.price_fixed if price > 0 else Setting.price_mode
        self.__pass_order(ctx, self.sell_code, self.type_order_by_total_ratio, code, pr_type, ratio, price, policy)

    def sell_by_available_ratio(self, ctx: Context, code: str, ratio: float, price: float = 0, policy: str = "") -> None:
        if ratio <= 0 or ratio > 1:
            raise ValueError(f"ratio should between 0~1")

        pr_type = self.price_fixed if price > 0 else Setting.price_mode
        self.__pass_order(ctx, self.sell_code, self.type_order_by_available_ratio, code, pr_type, ratio, price, policy)

    def order_target_ratio(self, ctx: Context, code: str, ratio: float, price: float = 0) -> None:
        if ratio < 0 or ratio > 1:
            raise ValueError(f"ratio should between 0~1")

        pr_type = "FIX" if price > 0 else ("LATEST" if Setting.price_mode == 5 else "COMPETE")
        self.log.log_info(f"order_target_ratio code:{code} with ratio:{ratio} with {pr_type} price:{price}", ctx)
        self.container.order_target_percent(code, ratio, pr_type, price, ctx.ContextInfo, self.id)

    def clear_holding(self, ctx: Context, code: str, price: float = 0) -> None:
        self.order_target_ratio(ctx, code, 0, price)

    def clear_holdings(self, ctx: Context, price: float = 0) -> None:
        codes = self.get_available_holding_codes()
        for code in codes:
            self.order_target_ratio(ctx, code, 0, price)
