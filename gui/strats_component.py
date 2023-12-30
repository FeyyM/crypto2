import tkinter as tk
import typing

from interface.styling import *

from conns.binance import BinClient
from conns.bitmex import BitClient

from strats import MAs, BO



class StratsComponent(tk.Frame):
    def __init__(self, root, binance: BinClient, bitmex: BitClient, 
                 *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.root = root
        self._exchanges = {'Binance': binance, 'Bitmex': bitmex}
        self._all_contracts = []
        self._all_timeframes = ['1m', '5m', '15m', '30m', '4h', '1h']

        for exch, client in self._exchanges.items():
            for sym in client.contracts:
                self._all_contracts.append(sym + ' _' + exch.capitalize())

        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP, fill=tk.X)

        self._api = api
        self._strats = []
        self._strat_vars = []
        self._strat_vars.append(tk.StringVar())


    
    