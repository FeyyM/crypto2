import tkinter as tk
import logging 

from bitmex_futures import  get_contracts


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")

stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)


if __name__ == '__main__':


    bitmex_contracts = get_contracts()

    root = tk.Tk()
    root.configure(bg="gray12")

    # grid(), pack()
    i = 0; j = 0

    calibri_font = ("Calibri", 11, "normal")

    for item in bitmex_contracts:
        label_widget = tk.Label(root, text=item, borderwidth=1, relief=tk.SOLID, 
                                width=13, bg="gray12", fg="steelBlue1", font = calibri_font)

        label_widget.grid(row=i, column=j, sticky="ew")

        if i == 10:
            j += 1
            i = 0
        else:
            i += 1

        # label_widget.pack(side=tk.LEFT)
        # label_widget.pack(side=tk.BOTTOM)
        # label_widget.pack(side=tk.TOP)

    root.mainloop()