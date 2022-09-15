from pandas.core.frame import DataFrame


class Context:
    def __init__(self, ContextInfo):
        self.ContextInfo = ContextInfo

    def get_bar_timetag(self) -> int:
        return self.ContextInfo.get_bar_timetag(self.ContextInfo.barpos)

    def get_stock_list_in_sector(self, sector: str) -> list[str]:
        return self.ContextInfo.get_stock_list_in_sector(sector)

    def get_all_codes(self) -> list[str]:
        return self.get_stock_list_in_sector('沪深A股')

    def get_market_data(self, fields: list[str], code: str, days: int) -> DataFrame:
        return self.ContextInfo.get_market_data(fields, stock_code=[code], period="1d", count=days)

    def do_back_test(self) -> bool:
        return self.ContextInfo.do_back_test

    def is_last_bar(self) -> bool:
        return self.ContextInfo.is_last_bar()

    def get_price(self, code: str) -> float:
        if self.do_back_test():
            return self.ContextInfo.get_market_data(["close"], stock_code=[code])
        else:
            return self.ContextInfo.get_full_tick(stock_code=[code])[code]["lastPrice"]

    def get_capital(self) -> float:
        return self.ContextInfo.capital
