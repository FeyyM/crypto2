import tkinter as tk

# from gui.root_component import Root
from gui.styling import BOLD_FONT, GLOBAL_FONT, BG_COLOR, FG_COLOR, BG_COLOR_2, FG_COLOR_2
from connectors.binance_futures import BinanceFuturesClient as bin
from connectors.bitmex import BitmexClient as bx
from strategies import TAma as TechnicalStrategy, TAbo as BreakoutStrategy
     

class StratEditor(tk.Frame):
    def __init__(self, root, binance: bin, bitmex: bx, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.root = root
        self._exchanges = {"Binance": binance} #, "Bitmex": bitmex}
        
        self._all_contracts = [sym + "_" + "Binance".capitalize() for sym in binance.contracts]
        self._all_timeframes = ["1m", "5m", "15m","30m", "1h", "4h"]

        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        self._add_button = tk.Button(self._commands_frame, text="Add strategy", 
                                     font=BOLD_FONT, command=self._add_strat_row, bg=BG_COLOR_2, fg=FG_COLOR)
        self._add_button.pack(side=tk.TOP)
        
        self._headers = ["Strategy", "Contract", "Timeframe", "Balance%", "TP%", "SL%"]

        self._strategy_detailed_parameters_from_input = {}
        self._extra_input = {}

        self._base_params = [
            {"code_name": "strategy_type", "widget": tk.OptionMenu, "width": 10,
             "data_type": str, "values": ["Technical", "Breakout"]},
            {"code_name": "contract", "widget": tk.OptionMenu, "width": 15,
             "data_type": str, "values": self._all_contracts},
            {"code_name": "timeframe", "widget": tk.OptionMenu, "width": 7,
             "data_type": str, "values": self._all_timeframes},
            {"code_name": "balance_pct", "widget": tk.Entry, "width": 7, "data_type": float},
            {"code_name": "take_profit", "widget": tk.Entry, "width": 7, "data_type": float},
            {"code_name": "stop_loss", "widget": tk.Entry, "width": 7, "data_type": float},
            {"code_name": "parameters", "widget": tk.Button, "data_type": float,
             "text": "Params", "bg": BG_COLOR_2, "command": self._show_popup},
            {"code_name": "activation", "widget": tk.Button,  "data_type": float,
             "text": "OFF", "bg": "darkred", "command": self._switch_strat},
            {"code_name": "delete", "widget": tk.Button, "data_type": float,
             "text": "X", "bg": "darkred", "command": self._delete_row}]

        self._strat_required_detailed_params = {"Technical": [
                {"code_name": "ema_fast", "name": "MACD Fast Length", "widget": tk.Entry, "data_type": int},
                {"code_name": "ema_slow", "name": "MACD Slow Length", "widget": tk.Entry, "data_type": int},
                {"code_name": "ema_signal", "name": "MACD Signal Length", "widget": tk.Entry, "data_type": int}
            ], "Breakout": [{"code_name": "min_volume", "name": "Minimum Volume",
                             "widget": tk.Entry, "data_type": float}]}

        for col_no, col_name in enumerate(self._headers):
            header = tk.Label(self._table_frame, text=col_name, bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0, column=col_no)

        self.body_widgets = {strat_el_dict['code_name']: {} for strat_el_dict in self._base_params}
        self.body_widgets.update({h + "_var": {} for h in ['strategy_type', "contract", "timeframe"]})

        self._body_table_last_row = 1


    def _add_strat_row(self):
        row = self._body_table_last_row

        for col_no, col_element in enumerate(self._base_params):
            code_name = col_element['code_name']
            if col_element['widget'] == tk.OptionMenu:
                self.body_widgets[code_name + "_var"][row] = tk.StringVar()
                self.body_widgets[code_name + "_var"][row].set(col_element["values"][0])
                self.body_widgets[code_name][row] = tk.OptionMenu(self._table_frame, self.body_widgets[code_name + "_var"][row],
                                                                  *col_element["values"])
                self.body_widgets[code_name][row].config(width=col_element['width'])
            
            elif col_element['widget'] == tk.Entry:
                self.body_widgets[code_name][row] = tk.Entry(self._table_frame, fg=FG_COLOR, bg=BG_COLOR,
                                       justify=tk.CENTER, insertbackground=FG_COLOR)

            elif col_element['widget'] == tk.Button:
                self.body_widgets[code_name][row] = tk.Button(self._table_frame, text=col_element['text'], bg=col_element['bg'], command=lambda frozen_command=col_element['command']:frozen_command(row), fg=FG_COLOR)
            else: 
                continue
            self.body_widgets[code_name][row].grid(row=row, column=col_no)

        # preparing room for storing additional parameters
        self._strategy_detailed_parameters_from_input[row] = {}

        for params in self._strat_required_detailed_params.values():
            for required in params:
                self._strategy_detailed_parameters_from_input[row][required['code_name']] = None

        # self._strategy_detailed_parameters_from_input[row].update({required['code_name']: None for params in self._strat_required_detailed_params.values() for required in params})

        self._body_table_last_row += 1


    def _show_popup(self, row: int):
        
        # gets coordinates used to show popup close to the button pressed
        coord_x = self.body_widgets["parameters"][row].winfo_rootx()
        coord_y = self.body_widgets["parameters"][row].winfo_rooty()

        self._popup_window = tk.Toplevel(self)
        self._popup_window.wm_title("Parameters")
        self._popup_window.config(bg=BG_COLOR)
        self._popup_window.attributes("-topmost", "true")
        self._popup_window.geometry(f"+{coord_x - 80 }+{coord_y + 30}")
        self._popup_window.grab_set()

        strat_type_selected = self.body_widgets['strategy_type_var'][row].get()

        #show elements of the popup interface (text and input for strategy details)        
        popup_row = 0
        for element in self._strat_required_detailed_params[strat_type_selected]:
            code_name = element['code_name']
            
            temp_label = tk.Label(self._popup_window, text=element["name"], bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
            temp_label.grid(row=popup_row, column=0)

            if element['widget'] == tk.Entry:
                self._extra_input[code_name] = tk.Entry(self._popup_window, bg=BG_COLOR_2, fg=FG_COLOR, justify=tk.CENTER, insertbackground=FG_COLOR)
                if self._strategy_detailed_parameters_from_input[row][code_name]:
                    self._extra_input[code_name].insert(tk.END, str(self._strategy_detailed_parameters_from_input[row]['code_name']))  
                self._extra_input[code_name].grid(row=popup_row, column=1)

            popup_row += 1

        # Validation button
        validation_button = tk.Button(self._popup_window, text="Validate", bg=BG_COLOR_2, fg=FG_COLOR, command=lambda: self._validate_params(row))
        validation_button.grid(row=popup_row, column=0, columnspan=2)


    def _validate_params(self, row: int):
        
        strat_selected = self.body_widgets['strategy_type_var'][row].get()
        for param in self._strat_required_detailed_params[strat_selected]:
            code_name = param['code_name']
            if self._extra_input[code_name].get() == "":
                self._strategy_detailed_parameters_from_input[row][code_name] = None
            else:
                self._strategy_detailed_parameters_from_input[row][code_name] = param['data_type'](self._extra_input[code_name].get())
        self._popup_window.destroy()


    def _switch_strat(self, row: int):
        for param in ["balance_pct", "take_profit", "stop_loss"]:
            if self.body_widgets[param][row].get() == "":
                self.root.logging_frame.add_log(f"Missing {param} parameter")
                return 

        strat_selected = self.body_widgets['strategy_type_var'][row].get()

        for param in self._strat_required_detailed_params[strat_selected]: 
            if self._strategy_detailed_parameters_from_input[row][param['code_name']] is None: 
                self.root.logging_frame.add_log(f"Missing {param['code_name']}")
                return

        symbol, exch = self.body_widgets['contract_var'][row].get().split("_")
        timeframe = self.body_widgets['timeframe_var'][row].get()
        
        # balance_pct = float(self.body_widgets['timeframe_var'][row])
        # take_profit = float(self.body_widgets['take_profit'][row])
        # stop_loss = float(self.body_widgets['stop_loss'][row])

        balance_pct, take_profit, stop_loss = [float(self.body_widgets[el][row].get())
                        for el in ('balance_pct', 'take_profit', 'stop_loss')]

        if self.body_widgets['activation'][row].cget("text") == "OFF":
            # activate strategy

            contract = self._exchanges[exch].contracts[symbol]

            if strat_selected == "Technical":
                new_strategy = TechnicalStrategy(contract, exch, timeframe, balance_pct,
                                                 take_profit, stop_loss, 
                                                 kwargs=self._strategy_detailed_parameters_from_input[row])
                
            elif strat_selected == "Breakout":
                new_strategy = BreakoutStrategy(contract, exch, timeframe, balance_pct,
                                                take_profit, stop_loss,
                                                kwargs=self._strategy_detailed_parameters_from_input[row])
                
            else:
                return

            new_strategy.candles = self._exchanges[exch].get_historical_candles(contract, timeframe)

            if not new_strategy.candles:
                self.root.logging_frame.add_log(f"No historacal data retrived for {contract.symbol}")
                return 
            
            self._exchanges[exch].strategies[row] = new_strategy

            for param in self._base_params:
                code_name = param['code_name']
                if code_name != "activation" and "_var" not in code_name:
                    self.body_widgets[code_name][row].config(state=tk.DISABLED)

            self.body_widgets['activation'][row].config(bg="darkgreen", text="ON")
            self.root.logging_frame.add_log(f"{strat_selected} on {symbol} with {timeframe} timeframe has started")

        else:
            # deactivate strategy
            # delete strategy object from connector
            del self._exchanges[exch].strategies[row]
            # delete elements of the interface
            for param in self._base_params:
                code_name = param['code_name']
                if code_name != "activation" and "_var" not in code_name:
                    self.body_widgets[code_name][row].config(state=tk.NORMAL)

            self.body_widgets['activation'][row].config(bg="darkred", text="OFF")
            self.root.logging_frame.add_log(f"{strat_selected} on {symbol} with {timeframe} timeframe has stopped")


    def _delete_row(self, row: int):
        for col in self.body_widgets.values():
            if type(col[row]) is not tk.StringVar:
                col[row].grid_forget()
            del col[row]
