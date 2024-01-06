import logging
from datetime import datetime as dt, time as tt, timedelta as td


from models import Contract, Candle


logger = logging.getLogger()
TF_EQUIV = {"1m":60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400}



class Strategy:
    def __init__(self, contract: Contract, exch, timeframe: str, balance_pct: float,
                 take_profit: float, stop_loss: float) -> None:
        self.contract = contract
        self.exchange = exch
        self.timeframe = timeframe
        self.tf_equiv = 1000*TF_EQUIV[timeframe] 
        self.balance_pct = balance_pct
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        # variable to store the candles
        self.candles: list[Candle] = []

    def parse_trade(self, price: float, size: float, timestamp: int):

        last_candle = self.candles[-1]

        # same candle
        if timestamp < last_candle.timestamp + self.tf_equiv:
            last_candle.close = price
            last_candle.vol += size

            if price > last_candle.high:
                last_candle.high = price
            elif price < last_candle.low:
                last_candle.low = price

            return 0 #no change in candles

        # mising at least one "empty candle"
        elif timestamp >= last_candle.timestamp + 2 * self.tf_equiv:
            missed_candles = int((timestamp - last_candle.timestamp) / self.tf_equiv) - 1 

            logger.info("%s and %s symbol missing %s candles %s timeframe (%s %s)", self.exchange, self.contract.symbol, missed_candles, self.timeframe, timestamp, last_candle.timestamp)
            new_ts = last_candle.timestamp + self.tf_equiv
            self.candles.append(Candle({"ts": new_ts, "open": price, "high": price, "low": price,
            "close": price, "vol": size}, exch="parser"))
            logger.info("%s New candle %s for with %s timeframe", self.exchange, self.contract.symbol, self.timeframe)
            for _ in range(missed_candles):
                new_ts = last_candle.timestamp + self.tf_equiv
                self.candles.append(Candle({"ts": new_ts, "open": last_candle.close,
                                           "high": last_candle.close, "low": last_candle.close, "close": last_candle.close, "vol": 0}))
                last_candle = self.candles[-1]
            
        # new candle
        elif timestamp >= last_candle.timestamp + self.tf_equiv:
            new_ts = last_candle.timestamp + self.tf_equiv
            self.candles.append(Candle({"ts": new_ts, "open": price, "high": price, "low": price,
            "close": price, "vol": size}, exch="parser"))
            logger.info("%s New candle %s for with %s timeframe", self.exchange, self.contract.symbol, self.timeframe)

        return 1 #new candles added, recalculate


class TAma(Strategy):
    def __init__(self, contract: Contract, exch, timeframe: str, balance_pct: float, 
                 take_profit: float, stop_loss: float, **kwargs) -> None:
        """Technical Analysis moving average strategy

        Args:
            contract (Contract): _description_
            exch (_type_): _description_
            timeframe (str): _description_
            balance_pct (float): _description_
            take_profit (float): _description_
            stop_loss (float): _description_
            
            Following variables are required in kwargs for the strategy to start
            ema_fast (integer): Number of fast periods
            ema_slow (integer): Number of slow periods
            ema_signal (integer): Number of signal period to take into account
        """

        super().__init__(contract, exch, timeframe, balance_pct, take_profit, stop_loss)

        self._ema_fast = kwargs.get('ema_fast')
        self._ema_slow = kwargs.get('ema_slow')
        self._ema_signal = kwargs.get('ema_signal')

        print("Activated TA strat", contract.symbol)


class TAbo(Strategy):
    def __init__(self, contract: Contract, exch, timeframe: str, balance_pct: float,
                 take_profit: float, stop_loss: float, **kwargs) -> None:
        """Technical Analysis breakout strategy

        Args:
            contract (Contract): _description_
            exch (_type_): _description_
            timeframe (str): _description_
            balance_pct (float): _description_
            take_profit (float): _description_
            stop_loss (float): _description_

            Following variables are required in kwargs for the strategy to start
            min_volume (integer): Minimal breakout volume for the strategy to work
            
        """
        super().__init__(contract, exch, timeframe, balance_pct, take_profit, stop_loss)


        self._min_vol = kwargs.get('min_volume')

    def _check_signal(self) -> int[-1, 0, 1]:
        if self.candles[-1].close > self.candles[-2].high and self.candles[-1].vol >= self._min_vol:
            return 1
        elif self.candles[-1].close < self.candles[-2].low and self.candles[-1].vol >= self._min_vol:
            return -1
        else:
            return 0


min_cost_effective_volume_sii = 1724.15
min_cost_effective_volume_regular = 1315.78

# candle = (tm, o, h, l, c, v)

class Strategy2:
    """Base strategy class for bossa api
    """
    def __init__(self, api, symbol: str, timeframe: str, balance_pct: float,
                 take_profit: float, stop_loss: float, isfutures=False) -> None:
        
        self.api = api
        self.symbo = symbol
        self.timeframe = timeframe
        self.secsC = td(seconds=TF_EQUIV[timeframe])
        self.balance_pct = balance_pct
        self.take_profit = take_profit
        self.stop_loss = stop_loss
        self._isfutures = isfutures
        self._tradStart = self._mtk_open()
        self.candles: list[tuple] = []
        

    def _mtk_open(self):
        openTm = tt.fromisoformat("08:45:00") if self._isfutures else tt.fromisoformat("09:00:00")
        return dt.combine(date=dt.today(), time=openTm)

    def parse_trade(self, trade: tuple) -> int[0, 1]:
        
        # candle = (tm, o, h, l, c, v, t)
        # c          0  1  2   3  4 5 6
        # trade
        px = float(trade[0])
        vol = int(trade[1])
        tm = dt.combine(date=dt.today(), time=tt.fromisoformat(trade[2]))
        trds = int(trade[3])
        
        if lastCandle := self.candles[-1]:
            # same candle
            if tm < lastCandle[0] + self.secsC:
                high = px if px > lastCandle[2] else lastCandle[2]
                low = px if px < lastCandle[3] else lastCandle[3]
                lastCandle = (lastCandle[0], lastCandle[1], high, low, px, 
                              lastCandle[3] + vol, lastCandle[6] + trds)
                return 0 #no change in candles

            # missing one candle
            elif tm < lastCandle[0] + 2*self.secsC:
                newCandle = (lastCandle[0] + self.secsC, px, px, px, px, vol, trds)
                self.candles.append(newCandle)

            # missing more candles
            else:
                misCandles = (dt.now() - lastCandle[0]) // TF_EQUIV[self.timeframe] - 1
                for _ in range(misCandles):
                    self.candles.append(lastCandle[0] + self.secsC, lastCandle[4], lastCandle[4], lastCandle[4], lastCandle[4], 0, 0)
                    lastCandle = self.candles[-1]
                self.candles.append((lastCandle[0] + self.secsC, px, px, px, px, px, vol, trds))
        
        # first candle
        else:
            tmDel = dt.now() - self._tradStart
            lostSeconds = (tmDel.seconds // TF_EQUIV[self.timeframe]) * TF_EQUIV[self.timeframe]
            curCnTm = self._tradStart + td(seconds=lostSeconds)
            self.candles.append((curCnTm, px, px, px, px, vol, trds))
        return 1 #change in candles    
        




class TAma2(Strategy2):
    def __init__(self, api, symbol: str, timeframe: str, balance_pct: float,
                 take_profit: float, stop_loss: float, **kwargs) -> None:
        super().__init__(api, symbol, timeframe, balance_pct, take_profit, stop_loss)

        self._ema_fast = kwargs.get('ema_fast')
        self._ema_slow = kwargs.get('ema_slow')
        self._ema_signal = kwargs.get('ema_signal')



class TAbo2(Strategy2):
    def __init__(self, api, symbol: str, timeframe: str, balance_pct: float,
                 take_profit: float, stop_loss: float, **kwargs) -> None:
        super().__init__(api, symbol, timeframe, balance_pct, take_profit, stop_loss)
        
        self._min_vol = kwargs.get('min_volume')

    
    def _check_signal(self) -> int[-1, 0, 1]:

        # candle = (tm, o, h, l, c, v, t)
        # c          0  1  2   3  4 5 6

        if self.candles[-1][4] > self.candles[-2][2] and self.candles[-1][5] >= self._min_vol:
            return 1
        elif self.candles[-1][4] < self.candles[-2][3] and self.candles[-1][5] >= self._min_vol:
            return -1
        else:
            return 0