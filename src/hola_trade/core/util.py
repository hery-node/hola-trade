from datetime import datetime


def get_share(money: float, price: float) -> int:
    return int((money // (price * 100)) * 100)
