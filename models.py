import datetime
import dateutil.parser as dup

BX_MULTIPLIER = 0.00000001
BX_TF_MINUTES = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}


def tick_to_decimals(tick_size: float) -> int:
    
    tick_size_str = "{0:8f}".format(tick_size)
    while tick_size_str[-1] == 0:
        tick_size_str = tick_size_str[:-1]
    
    split_tick = tick_size_str.split(".")

    if len(split_tick) > 1:
        return len(split_tick)
    else:
        return 0


class Balance:
    def __init__(self, info: dict, exch: str) -> None:
        if exch == "bi":
            self.initial_margin = float(info['initialMargin'])
            self.maintenance_margin = float(info['maintMargin'])
            self.margin_balance = float(info['marginBalance'])
            self.wallet_balance = float(info['walletBalance'])
            self.unrealized_pnl = float(info['unrealizedProfit'])
        elif exch == "bx":
            self.initial_margin =  BX_MULTIPLIER * info['initMargin']
            self.maintenance_margin = BX_MULTIPLIER * info['maintMargin']
            self.margin_balance = BX_MULTIPLIER * info['marginBalance']
            self.wallet_balance = BX_MULTIPLIER * info['walletBalance']
            self.unrealized_pnl = BX_MULTIPLIER * info['unrealisedPnl']


class Candle:
    def __init__(self, info: dict, exch: str, timeframe: str = None) -> None:
        if exch == "bi":
            self.timestamp = info[0]
            self.open = float(info[1])
            self.high = float(info[2])
            self.low = float(info[3])
            self.close = float(info[4])
            self.vol = float(info[5])
        elif exch == "bx":
            self.timestamp = dup.isoparse(info['timestamp']) - \
                datetime.timedelta(minutes=BX_TF_MINUTES.get(timeframe, 0))
            self.timestamp = int(self.timestamp.timestamp() * 1000)
            self.open = info['open']
            self.high = info['high']
            self.low = info['low']
            self.close = info['close']
            self.vol = info['volume']
            # print("orig: ", info['timestamp'], '\n', "after: ", self.timestamp,
            #       '\n', "parsed: ", dup.isoparse(info['timestamp']))
        elif exch == "parser":
            self.timestamp = info['ts']
            self.high = info['high']
            self.low = info['low']
            self.close = info['close']
            self.vol = info['volume']



class Contract:
    def __init__(self, info: dict, exch: str) -> None:
        if exch == "bi":
            self.symbol = info['symbol']
            self.base_asset = info['baseAsset']
            self.quote_asset = info['quoteAsset']
            self.price_decimals = info['pricePrecision']
            self.quantity_decimals = info['quantityPrecision']
            self.tick_size = pow(10, -info['pricePrecision'])
            self.lot_size = pow(10, -info['quantityPrecision'])

        elif exch == "bx":
            self.symbol = info['symbol']
            self.base_asset = info.get('rootSymbol')
            self.quote_asset = info.get('quoteCurrency')
            self.tick_size = info.get('tickSize')
            self.lot_size = info.get('lotSize')
            self.price_decimals = tick_to_decimals(self.tick_size)
            self.quantity_decimals = tick_to_decimals(self.lot_size)


class OrderStatus: 
    def __init__(self, info: dict, exch: str) -> None:
        if exch == "bi":
            self.order_id = info['orderId']
            self.status = info['status']
            self.avg_price = float(info['avgPrice'])
        elif exch == "bx":
            self.order_id = info['orderID']
            self.status = info['ordStatus']
            self.avg_price = info['avgPx']