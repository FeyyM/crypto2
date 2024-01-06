import tkinter as tk

from models import Contract
from gui.styling import BG_COLOR, FG_COLOR, GLOBAL_FONT, BOLD_FONT, BG_COLOR_2, FG_COLOR_2


class Watchlist(tk.Frame):
    def __init__(self, bin_contracts: dict[str, Contract], bx_contracts: dict[str, Contract],
                 *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


        # list of avaliable symbols
        self.bin_symbols = list(bin_contracts.keys())
        self.bx_symbols = list(bx_contracts.keys()) if bx_contracts else []
        # print(self.bin_symbols)

        # top frame
        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        # table frame
        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        # 2 entry boxes
        self._binance_label = tk.Label(self._commands_frame, text="Binance", 
                                       bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
        self._binance_label.grid(row=0, column=0)
        self._binance_entry = tk.Entry(self._commands_frame, fg=FG_COLOR, bg=BG_COLOR_2,
                                       justify=tk.CENTER, insertbackground=FG_COLOR)
        self._binance_entry.bind("<Return>", self._add_binance_method)
        self._binance_entry.grid(row=1,column=0)


        self._bitmex_label = tk.Label(self._commands_frame, text="Bitmex",
                                      bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
        self._bitmex_label.grid(row=0, column=1)
        self._bitmex_entry = tk.Entry(self._commands_frame, fg=FG_COLOR, bg=BG_COLOR_2,
                                      justify=tk.CENTER, insertbackground=FG_COLOR)
        self._bitmex_entry.bind("<Return>", self._add_bitmex_method)
        self._bitmex_entry.grid(row=1, column=1)


        # lower part of the watchlist frame dynamically created in a loop
        # header of the table with data
        self._headers = ["Symbol", "Exchange", "Bid", "Ask", "Remove"]
        for no, h in enumerate(self._headers):
            header = tk.Label(self._table_frame, text=h.capitalize() if h != "remove" else "", bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0, column=no)

        self._body_table_last_row = 1 #row 0 is occupied by self._headers
        self.body_widgets = {h:dict() for h in self._headers + ["Bid_var", "Ask_var"]}

    def _add_symbol(self, symbol: str, exch: str):
        
        row_index = self._body_table_last_row

        self.body_widgets['Symbol'][row_index] = tk.Label(self._table_frame, font=GLOBAL_FONT,
                                                          text=symbol, bg=BG_COLOR, fg=FG_COLOR_2)
        self.body_widgets['Symbol'][row_index].grid(row=row_index, column=0)

        self.body_widgets['Exchange'][row_index] = tk.Label(self._table_frame, font=GLOBAL_FONT,
                                                            text=exch, bg=BG_COLOR, fg=FG_COLOR_2)
        self.body_widgets['Exchange'][row_index].grid(row=row_index, column=1)

        self.body_widgets['Bid_var'][row_index] = tk.StringVar()
        self.body_widgets['Bid'][row_index] = tk.Label(self._table_frame,
                                                       textvariable=self.body_widgets['Bid_var'][row_index],
                                                       font=GLOBAL_FONT, bg=BG_COLOR, fg=FG_COLOR_2)
        self.body_widgets['Bid'][row_index].grid(row=row_index, column=2)

        self.body_widgets['Ask_var'][row_index] = tk.StringVar()
        self.body_widgets['Ask'][row_index] = tk.Label(self._table_frame,
                                                       textvariable=self.body_widgets['Ask_var'][row_index],
                                                       font=GLOBAL_FONT, bg=BG_COLOR, fg=FG_COLOR_2)
        self.body_widgets['Ask'][row_index].grid(row=row_index, column=3)

        self.body_widgets['Remove'][row_index] = tk.Button(self._table_frame, text="X",
                                                           font=BOLD_FONT, bg="darkred", fg=FG_COLOR,
                                                           command=lambda: self._remove_symbol(row_index))
        self.body_widgets['Remove'][row_index].grid(row=row_index, column=4)

        self._body_table_last_row += 1


    def _remove_symbol(self, row_index: int):
        for column in self._headers:
            self.body_widgets[column][row_index].grid_forget()
            del self.body_widgets[column][row_index]
        del self.body_widgets["Ask_var"][row_index]
        del self.body_widgets["Bid_var"][row_index]

    def _add_binance_method(self, event):
        symbol = event.widget.get()
        if symbol in self.bin_symbols:
            self._add_symbol(symbol, "Bin")
            event.widget.delete(0, tk.END)


    def _add_bitmex_method(self, event):
        symbol = event.widget.get()
        if symbol in self._bin_symbols:
            self._add_symbol(symbol, "Bx")
            event.widget.delete(0, tk.END)
        
