from datetime import datetime as dt
import tkinter as tk

from gui.styling import BG_COLOR, FG_COLOR, GLOBAL_FONT


class LoggingC(tk.Frame):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logging_text = tk.Text(self, height=20, width=60, state=tk.DISABLED,
                                    bg=BG_COLOR, fg=FG_COLOR, font=GLOBAL_FONT)
        self.logging_text.pack(side=tk.TOP)


    def add_log(self, msg: str):
        self.logging_text.configure(state=tk.NORMAL)
        self.logging_text.insert("1.0", dt.now().strftime("%a %H:%M:%S :: ") + msg + "\n")
        self.logging_text.configure(state=tk.DISABLED)
