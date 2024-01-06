import logging
import tkinter as tk

from connectors.binance_futures import BinanceFuturesClient
from connectors.bitmex import BitmexClient
from gui.root_component import Root

from conns.binance import BinClient
from models import Contract



logger = logging.getLogger()

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# stream logger
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

# file logger
file_handler = logging.FileHandler("info.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)



if __name__ == '__main__':


    # print(binance.get_contracts())
    # print(binance.get_bid_ask("BTCUSDT"))
    # print(binance.get_historical_candles("BTCUSDT", "1h"))
    # print(bix.contracts['XBTUSD'].base_asset)
    # bix.get_historical_candles(Contract({'symbol': 'XBTUSD'}, "bx"), "1h")
    binance = BinanceFuturesClient("", "", True)
    bix = BitmexClient("uXr1T711wD-3pvEpXjlkvNFx", "GEIkARqi2QZh70V77T28M2Y0zxSB_rNGhRJIbwZAIqYCkYu", True)
    root = Root(binance, bix)
    root.mainloop()