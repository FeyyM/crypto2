import logging
import typing
import time

import pandas as pd


from models. import Candle


logger = logging.getLogger()


TF_EQUIV = {'1m': 60, '5m': 300, '15m': 900, '30m': 1800, '1h': 3600,
            '4h': 14400}



class Strategy:
    def __init__(self, api, instrument, timeframe: str, balance_pct: float, 
                 take_profit: float, stop_loss: float) -> None:
        
        self.api = api
        self.instrument = instrument
        self.timeframe = TF_EQUIV[timeframe]
        self.balance_pct = balance_pct
        self.take_profit = take_profit 
        self.stop_loss = stop_loss

        self._trades = []
        self._orders = []
        self.open_position = None
        self._balance = None
        self._profit = None
        self._loss = None

        self.candles: typing.List[Candle] = []



    def intitial_candle(self) -> None:
        
        time.time.now()

        time.time.now()
        
        pass

    def parse_trade(self, price: float, size: float, timestamp: int) -> int:

        timestamp_diff = int(time.time() * 1000) - timestamp
        if timestamp_diff >= 2000:
            logger.warning("%s delay by %s miliseconds",
                           self.instrument, timestamp_diff)


        # if self.candles:
        last_candle = self.candles[-1]
        
        # current candle

        if timestamp < last_candle.timestap + self.timeframe:
            last_candle.close = price
            last_candle.vol =+ size

            if last_candle.high < price:
                last_candle.high = price
            elif last_candle.low > price:
                last_candle.low = price
        
            return 0

        elif timestamp < last_candle.timestamp + 2 * self.timeframe:
            
            new_ts = last_candle.timestamp + self.timeframe
            candle_info = {'t': new_ts, 'o': price, 'h': price, 'l': price,
                           'c': price, 'v': price}
            new_candle = Candle(candle_info, self.timeframe, "trade")
            self.candles.append(new_candle)


        # missing candles
        else:
            missing_candles = int((timestamp - last_candle.timestamp) // self.timeframe) - 1

            for missing in range(missing_candles):
                new_ts = last_candle.timestamp + self.timeframe
                candle_info = {'t': new_ts, 'o': last_candle.close,
                               'h': last_candle.close, 'l': last_candle.close,
                               'c': last_candle.close, 'v': 0}
                self.candles.append(Candle(candle_info, self.timeframe, "trade"))
                last_candle = self.candles[-1]

        return 1

    def _open_position(self, signal: int):
        
        trade_size = self.api.get_trade_size(self.contract, self.candles[-1].close,
                                self.balance_pct)
    
        if trade_size is None:
            return 
        els




class MAs(Strategy):
    def __init__(self, api, instrument, timeframe: str, balance_pct: float,
                 take_profit: float, stop_loss: float, **kwargs) -> None:
        super().__init__(api, instrument, timeframe, balance_pct, take_profit, stop_loss)

        self._ema_fast = kwargs.get('ema_fast')
        self._ema_slow = kwargs.get('ema_slow')
        self._ema_signal = kwargs.get('ema_signal')
        self._rsi_length = kwargs.get('rsi_length')

    def _compute_closes(self):
        self._closes = pd.Series([c.close for c in self.candles])

    
    def _macd(self) -> tuple[float, float]:
        self._compute_closes()
        ema_fast = self._closes.ewm(span = self._ema_fast).mean()
        ema_slow = self._closes.ewm(span = self._ema_slow).mean()
        macd_line = ema_fast - ema_slow
        macd_signal = macd_line.ewm(span = self._ema_signal).mean()
        return macd_line.iloc[-2], macd_signal.iloc[-2]
        

    def _rsi(self):
        delta = self._closes.diff().dropna()
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        avg_gain = up.ewm(com = (self._rsi_length - 1), min_periods=self._rsi_length).mean()
        avg_loss = down.abs().ewm(com = (self._rsi_length - 1), min_periods=self._rsi_length).mean()
        rsi = 100 - 100 / (1 + avg_gain / avg_loss)
        rsi = rsi.round(2)
        return rsi.iloc[-2]


    def _check_signal(self):
        
        macd_line, macd_signal = self._macd()
        rsi = self._rsi()

        if rsi < 30 and macd_line > macd_signal:
            return 1
        elif rsi > 70 and macd_line < macd_signal:
            return -1 
        else:
            return 0


    def check_trade(self, tick_type: int):

        if not self.open_position and tick_type == 1: #new candle, update calculations
            signal_result = self._check_signal()
        
            if signal_result != 0:
                self._open_position(signal_result)


    



class BO(Strategy):
    def __init__(self, api, instrument, timeframe: str, balance_pct: float,
                 take_profit: float, stop_loss: float, **kwargs) -> None:
        super().__init__(api, instrument, timeframe, balance_pct, take_profit, stop_loss)

        self._min_vol = kwargs.get('min_vol')


    def _check_signal(self) -> int:

        if self.candles[-1].close > self.candles[-2].high and \
            self.candles[-1].vol > self._min_vol:
            return 1
        elif self.candles[-1].close > self.candles[-2].low and \
            self.candles[-1].vol > self._min_vol:
            return -1
        else:
            return 0
        

    def _check_trade(self, tick_type: int):
        
        if not self.open_position:
            if signal_results := self._check_signal():
                self._open_position(signal_results)


class InsideBar(Strategy):
    def __init__(self, instrument, timeframe: str, balance_pct: float,
                 take_profit: float, stop_loss: float, **kwargs) -> None:
        super().__init__(instrument, timeframe, balance_pct, take_profit, stop_loss)

        self._min_vol = kwargs.get('min_vol')

    def _check_signal(self) -> int:
        if self.candles[-3].high > self.candles[-2].high and \
            self.candles[-3].low < self.candles[-2].low:

            if self.candles[-1].close > self.candles[-3].high:
                return 1
            elif self.candles[-1].close > self.candles[-3].low:
                return -1
            
        return 0

        
class OutsideBar(Strategy):
    def __init__(self, instrument, timeframe: str, balance_pct: float,
                 take_profit: float, stop_loss: float, **kwargs) -> None:
        super().__init__(instrument, timeframe, balance_pct, take_profit, stop_loss)

        self._min_vol = kwargs.get('min_vol')

    def _check_signal(self) -> int:
        if self.candles[-3].high < self.candles[-2].high and \
            self.candles[-3].low > self.candles[-2].low:

            if self.candles[-1].close > self.candles[-3].high:
                return 1
            elif self.candles[-1].close > self.candles[-3].low:
                return -1
            
        return 0