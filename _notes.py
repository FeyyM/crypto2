# import time

# u = 10.0 // 2.5
# print(u)
# print(type(u))


# signal = -1

# if signal:
#     print("signal")


# print(time.strftime("%H:%M:%OS", time.time()))

# # time.time().strftime()

# # time.strftime


# time.strftime()

# channel = "kanel"
# contracts = ["BTC", "USD"]

# print({'method': 'SUBSCRIBE', #'id': self._ws_id,
#                                        'params': [contract.lower() + "@" + channel
#                                                   for contract in contracts]})


# tst_dict = {"a": "A", "b": "B"}
# print(tst_dict["a"])
# print(tst_dict[None])


# print(pow(10,2), "|", pow(10,-2))


# di = {"this": "it", "that": "not"}


# print(di.get())

from datetime import datetime as dt, time as tt, timedelta as td

# a = dt.today()
futures = True

TF_EQUIV = {"1m":60, "5m": 300, "15m": 900, "30m": 1800, "1h": 3600, "4h": 14400}

tmFr = "15m"

tradStart = "08:45:00" if futures else "09:00:00" 
openTm = dt.combine(date=dt.today(), time=tt.fromisoformat(tradStart))
print("Open time: ", openTm.time())

currTm = dt.now()

timeD = currTm - openTm
print("Candle periods from start: ", timeD.seconds / TF_EQUIV[tmFr])
print("Full cnalde periods from start: ", timeD.seconds // TF_EQUIV[tmFr])
print("Number of seconds", timeD.seconds)

currCandle = openTm + td(seconds=(timeD.seconds // TF_EQUIV[tmFr]) * TF_EQUIV[tmFr])
print("Current candle time:", currCandle.strftime("%H:%M:%S"))


uno = [("01", "aba"), ("02", "baba"), ("03", "zaba")]

uno[-1] = ("04", "cobo")

print(uno)



# c = dt.fromisoformat('04:23:01')

# c = tt.fromisoformat('04:23:01')
# a = tt.fromisoformat('09:00:00')

# print(a, b, c, a-b, a-c)