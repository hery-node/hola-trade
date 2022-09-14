class ContextInfo:
    def __init__(self, ctx_info):
        self.ctx_info = ctx_info

    def get_bar_timetag(self) -> int:
        return self.ctx_info.get_bar_timetag(self.ctx_info.barpos)

    def get_stock_list_in_sector(self, sector: str) -> list[str]:
        return self.ctx_info.get_stock_list_in_sector(sector)

    def get_all_codes(self) -> list[str]:
        return self.get_stock_list_in_sector('沪深A股')

    def get_market_data(self, fields: list[str], code: str, days: int):
        return self.ctx_info.get_market_data(fields, stock_code=[code], period="1d", count=days)

    def do_back_test(self) -> bool:
        return self.ctx_info.do_back_test()

    def get_price(self, code: str) -> float:
        if self.do_back_test():
            return self.ctx_info.get_market_data(["close"], stock_code=[code])
        else:
            return self.ctx_info.get_full_tick(stock_code=[code])[code]["lastPrice"]
