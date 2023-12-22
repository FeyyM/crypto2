import tkinter as tk
import logging
from conns.bitmex import get_contracts
from conns.binance import BinClient


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


logger.debug("Debug info")
logger.info("Info info")
logger.warning("Warning info")
logger.error("Error info")


if __name__ == "__main__":
    logger.info("Main loop")

    binc = BinClient("public", "secret", True)
    print(binc.get_historical_candles("BTCUSDT", "1h"))


    # btmx_contracts = get_contracts()
    # root = tk.Tk()
    # root.configure(bg = "black")
    # i = 0
    # cl = 0

    # cal_font = ("Calibri", 11, "normal")

    # for contract in btmx_contracts:
    #     label_widget = tk.Label(root, text = contract, borderwidth=1, font = cal_font,
    #                             bg = "gray12", fg = "SteelBlue1", relief=tk.SOLID)
    #     # label_widget.pack(side = tk.LEFT)
    #     label_widget.grid(row = i, column=cl, sticky="ew")
        
    #     if i == 10:
    #         cl += 1
    #         i = 0
    #     else:
    #         i += 1


    # root.mainloop()

