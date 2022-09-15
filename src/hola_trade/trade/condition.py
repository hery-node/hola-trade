from abc import ABC, abstractmethod
from hola_trade.core.ctx import Context


class Condition(ABC):
    @abstractmethod
    def filter_codes(self, ctx: Context, codes: list[str]) -> list[str]:
        # write your policy code here
        pass


class PolicyConditions:
    def __init__(self, select_condition: Condition, buy_condition: Condition, sell_condition: Condition, add_condition: Condition, clear_condition: Condition) -> None:
        self.select_condition = select_condition
        self.buy_condition = buy_condition
        self.sell_condition = sell_condition
        self.add_condition = add_condition
        self.clear_condition = clear_condition
