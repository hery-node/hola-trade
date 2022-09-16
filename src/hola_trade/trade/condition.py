from abc import ABC, abstractmethod
from hola_trade.core.ctx import Context


class Target:
    def __init__(self, code, value) -> None:
        self.code = code
        self.value = value


class Condition(ABC):
    @abstractmethod
    def filter(self, ctx: Context, codes: list[str]) -> list[Target]:
        # write your policy code here
        pass


class PolicyConditions:
    def __init__(self, select_condition: Condition, buy_condition: Condition, add_condition: Condition, sell_condition: Condition,  clear_condition: Condition) -> None:
        self.select_condition = select_condition
        self.buy_condition = buy_condition
        self.add_condition = add_condition
        self.sell_condition = sell_condition
        self.clear_condition = clear_condition
