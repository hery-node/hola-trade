def get_share(money: float, price: float) -> int:
    return int((money // (price * 100)) * 100)


def get_today() -> str:
    import datetime
    # Get current date and time
    x = datetime.datetime.now()
    return str(x)[:10]
