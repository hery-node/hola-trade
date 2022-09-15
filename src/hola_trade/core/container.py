class Container:
    def __init__(self, timetag_to_datetime, get_trade_detail_data, order_value, order_shares):
        self.timetag_to_datetime = timetag_to_datetime
        self.get_trade_detail_data = get_trade_detail_data
        self.order_value = order_value
        self.order_shares = order_shares
