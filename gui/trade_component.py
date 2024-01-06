import tkinter as tk

from gui.styling import BG_COLOR, FG_COLOR, GLOBAL_FONT, BOLD_FONT, FG_COLOR_2


class TradeWatch(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._headers = ["time", "symbol", "exchange", "strategy", "side", "quantity", "status", "pnl"]
        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        # dict with body widgets
        self.body_widgets = {item: dict() for item in self._headers}
        self.body_widgets.update({"Status_var": dict(), "Pnl_var": dict()})
        
        # top row
        for col_no, col_name in enumerate(self._headers):
            header = tk.Label(self._table_frame, text=col_name.capitalize(), bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
            header.grid(row=0, column=col_no)

        self._body_table_last_row = 1


    def add_trade(self, data: dict):
        
        row_index = self.body_widgets
        time_index = data['time']
        
        for col_no, col_name in enumerate(self._headers):
            if col_name in ["status", "pnl"]:
                self.body_widgets[col_name + "_var"][time_index] = tk.StringVar()
                self.body_widgets[col_name][time_index] = tk.Label(self._table_frame, bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT,
                    textvariable=self.body_widgets[col_name + "_var"][time_index])
                self.body_widgets[col_name][time_index].grid(row=row_index, col=col_name)
                continue

            self.body_widgets[col_name][time_index] = tk.Label(self._table_frame, text=data[col_name], bg=BG_COLOR, fg=FG_COLOR_2, font=GLOBAL_FONT)
            self.body_widgets[col_name][time_index].grid(row=row_index, column=col_no)
            

        

        self._body_table_last_row += 1