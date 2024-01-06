import time
import tkinter as tk
import logging

from gui.styling import BG_COLOR
from gui.logging_component import LoggingC
from gui.watchlist_component import Watchlist
from gui.trade_component import TradeWatch
from gui.strategy_component import StratEditor

from connectors.binance_futures import BinanceFuturesClient
from connectors.bitmex import BitmexClient

logger = logging.getLogger()



class Root(tk.Tk):
    def __init__(self, bi: BinanceFuturesClient, bx: BitmexClient) -> None:
        super().__init__()
        self.title("Trading Bot")
        self.configure(bg =BG_COLOR)
        
        self.binance = bi
        self.bitmex = bx
        # left frame
        self._left_frame = tk.Frame(self, bg=BG_COLOR)
        self._left_frame.pack(side=tk.LEFT)

        # right
        self._right_frame = tk.Frame(self, bg=BG_COLOR)
        self._right_frame.pack(side=tk.LEFT)

        # place watchlist component on the left frame
        self._watchlist_frame = Watchlist(bi.contracts, bx.contracts, 
                                          self._left_frame, bg=BG_COLOR)
        self._watchlist_frame.pack(side=tk.TOP)
        # place logging component on the left frame
        self.logging_frame = LoggingC(self._left_frame, bg=BG_COLOR)
        self.logging_frame.pack(side=tk.TOP)

        # strategy coponent on the right frame
        self._strat_frame = StratEditor(self, bi, bx, self._right_frame, bg=BG_COLOR)
        self._strat_frame.pack(side=tk.TOP)

        # place trade watch compoenent on the right frame
        self._tradewatch_frame = TradeWatch(self._right_frame, bg=BG_COLOR)
        self._tradewatch_frame.pack(side=tk.TOP)



        self._update_ui()


        # self._logging_frame.add_log("This is a test message")
        # time.sleep(3)
        # self._logging_frame.add_log("Another super duper test text message")

    def _update_ui(self):
        
        # checks logs in bitmex and bianance to show them
        for log in self.binance.logs:
            if not log['displayed']:
                self.logging_frame.add_log(log['msg'])
                log['displayed'] = True

        for log in self.bitmex.logs:
            if not log['displayed']:
                self.logging_frame.add_log(log['msg'])
                log['displayed'] = True

        # upadtes bid and ask prices for watchlist table
        
        try:
            for key_row_no in self._watchlist_frame.body_widgets['Symbol']:
                sym = self._watchlist_frame.body_widgets['Symbol'][key_row_no].cget("text")
                exch = self._watchlist_frame.body_widgets['Exchange'][key_row_no].cget("text")

                if exch == "Bin":
                    if sym not in self.binance.contracts:
                        continue
                    if sym not in self.binance.prices:
                        self.binance.get_bid_ask(self.binance.contracts[sym])
                    precision = self.binance.contracts[sym].price_decimals
                    prices = self.binance.prices[sym]
                elif exch == "Bx":
                    if sym not in self.bitmex.contracts:
                        continue
                    if sym not in self.bitmex.prices:
                        continue
                    precision = self.bitmex.contracts[sym].price_decimals
                    prices = self.bitmex.prices[sym]
                else:
                    continue

                if prices['bid']:
                    price_str = "{0:.{prec}}f".format(prices['bid'], prec=precision)
                    self._watchlist_frame.body_widgets['Bid_var'][key_row_no].set(price_str)
                
                if prices['ask']:
                    price_str = "{0:.{prec}}f".format(prices['ask'], prec= precision)
                    self._watchlist_frame.body_widgets['Ask_var'][key_row_no].set(price_str)
        except RuntimeError as e:
            logger.error("Error while looping througn watchlist dictionary: %s", e)


        self.after(2000, self._update_ui)



