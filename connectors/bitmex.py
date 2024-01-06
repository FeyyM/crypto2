import logging
import requests
import time
import json
import threading
import dateutil.parser
import typing

from urllib.parse import urlencode
import hmac
import hashlib
import websocket

from models import Candle, Contract, Balance, OrderStatus
from strategies import TAma as TechnicalStrategy, TAbo as BreakoutStrategy


logger = logging.getLogger()


class BitmexClient():
    def __init__(self, public_key: str, private_key: str, testnet: bool = True) -> None:
        
        stem = "//testnet.bitmex.com" if testnet else "//www.bitmex.com"
        self._base_url = f"https:{stem}"
        self._wss_url = f"wss:{stem}/realtime"
        self._public_key = public_key
        self._private_key = private_key
        
        self._ws = None
        self.contracts = self.get_contracts()
        self.balances = self.get_balances()

        self.logs = []

        self.strategies: dict[str, typing.Union[TechnicalStrategy, BreakoutStrategy]] = {}
        self.prices = dict()
        t = threading.Thread(target=self._start_ws); t.start()
        logger.info("Bitmex connector has been initialized")


    def _start_ws(self):
        self._ws = websocket.WebSocketApp(self._wss_url, on_message=self._on_message,
                                          on_open=self._on_open, on_close=self._on_close,
                                          on_error=self._on_error)
        while True:
            try:
                self._ws.run_forever()
            except Exception as e:
                logger.error("Bitmex error in run_forever() method %s", e)
            time.sleep(3)


    def _on_open(self, ws):
        logger.info("Bitmex connection opened")
        self._subscribe_channel("instrument")
        self._subscribe_channel("trade")


    def _on_close(self, ws):
        logger.warning("Bitmex Websocket connection closed")


    def _on_error(self, ws, msg: str):
        logger.error("Bitmex connection error: %s", msg)


    def _on_message(self, ws, msg: str):
        data = json.loads(msg)
        
        if data.get('table') == 'instrument':
            for d in data.get('data'):
                # print(d)
                if to_upd := d.get('bidPrice'):
                    self.prices.update({d['symbol']: {'bid': to_upd}})
                elif to_upd := d.get('askPrice'):
                    self.prices.update({d['symbol']: {'ask': to_upd}})
        elif data.get('table') == 'trade':
            for d in data.get('data'):
                for strat in self.strategies.values():
                    if strat.contract.symbol == d['symbol']:
                        ts = int(dateutil.parser.isoparse(d['timestamp']).timestamp() * 1000)
                        strat.parse_trade(d['price'], d['size'], ts)



    def _subscribe_channel(self, topic: str):
        try: 
            self._ws.send(json.dumps({'op': 'subscribe', 'args': [topic]}))
        except Exception as e:
            logger.error("Websocket error while subscribing to %s topic: %s", topic, e)


    def _generate_sig(self, method: str, endpoint: str, expires: str, payload: dict) -> str:
        message = method + endpoint + "?" + urlencode(payload) + expires
        return hmac.new(self._private_key.encode(), message.encode(), hashlib.sha256).hexdigest()


    def _make_request(self, method: str, endpoint: str, data: dict):
        
        headers = {'api-expires': str(int(time.time() + 5)), 'api-key': self._public_key}
        headers['api-signature'] = self._generate_sig(method, endpoint,
                                                      expires=headers["api-expires"], payload=headers)
        
        if method == "GET":
            try: 
                resp = requests.get(self._base_url + endpoint, params=data,
                                    headers=headers)
            except Exception as e:
                logger.error("Bitmex connection error while makin %s request to %s: %s", method, endpoint, e)
        elif method == "POST":
            try: 
                resp = requests.post(self._base_url + endpoint, params=data,
                                    headers=headers)
            except Exception as e:
                logger.error("Bitmex connection error while makin %s request to %s: %s", method, endpoint, e)
        elif method == "DELETE":
            try: 
                resp = requests.delete(self._base_url + endpoint, params=data,
                                    headers=headers)
            except Exception as e:
                logger.error("Bitmex connection error while makin %s request to %s: %s", method, endpoint, e)
        else:
            raise ValueError()
        
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error("Error while making %s request to %s: %s (error code %s)", 
                         method, endpoint, resp.json(), resp.status_code)


    def get_contracts(self) -> dict[str, Contract]:
        instruments = self._make_request("GET", "/api/v1/instrument/active", dict())
        if instruments:
            return {s['symbol']: Contract(s, "bx") for s in instruments}


    def get_balances(self) -> dict[str, Balance]:
        if margin_data := self._make_request("GET", "/api/v1/user/margin", {'currency': 'all'}):
            return {a['currency']: Balance(a, "bx") for a in margin_data}


    def place_order(self, contract: Contract, order_type: str, quantity: int, 
                    side: str, price=None, tif=None) -> OrderStatus:
        data = {'symbol': contract.symbol, 'side': side.capitalize(),
                'orderQty': round(quantity / contract.lot_size) * contract.lot_size,
         'ordType': order_type.capitalize()}
        if price: 
            data['price'] = round(price / contract.tick_size) * contract.tick_size
        if tif:
            data['timeInForce'] = tif

        if ord_status := self._make_request("POST", "/api/v1/order", data):
            return OrderStatus(ord_status, "bx")


    def get_order_status(self, order_id: str, contract: Contract) -> OrderStatus:
        if order_status := self._make_request("GET", "/api/v1/order", {'symbol': contract.symbol, 'reverse': True}):
            for order in order_status:
                if order['orderId'] == order_id:
                    return OrderStatus(order, "bx")


    def cancel_order(self, order_id: str) -> OrderStatus:
        if order_status := self._make_request("DELETE", "/api/v1/order", {'orderID': order_id}):
            return OrderStatus(order_status[0], "bx")


    def get_historical_candles(self, contract: Contract, timeframe: str) -> list[Candle]:
        if raw_candles := self._make_request("GET", "/api/v1/trade/bucketed", 
            {'symbol': contract.symbol, 'partial': True, 'binSize': timeframe, 'count': 500, 'reverse': True}):
            return [Candle(c, "bx", timeframe) for c in raw_candles]
        
    
    def _add_log(self, msg: str):
        logger.info("%s", msg)
        self.logs.append({"log": msg, "displayed": False})