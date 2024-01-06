import logging
import time
from urllib.parse import urlencode
import threading
import json

import hmac
import hashlib
import requests
import websocket
import typing


from models import Balance, Candle, Contract, OrderStatus
from strategies import TAma as TechnicalStrategy, TAbo as BreakoutStrategy


logger = logging.getLogger()


class BinanceFuturesClient:
    def __init__(self, public_key: str, secret_key: str, testnet: bool) -> None:
        self._base_url = "https://testnet.binancefuture.com" if testnet else \
            "https://fapi.binance.com"
        self._wss_url = "wss://stream.binancefuture.com/ws" if testnet else \
            "wss://fstream.binance.com/ws"

        logger.info("Binance Futures Client succesfully initialized")
        self._public_key = public_key
        self._secret_key = secret_key
        self._headers = {"X-MBX-APIKEY": self._public_key}
        

        self.contracts = self.get_contracts()
        # self.balances = self.get_balances()
        self.prices = {}
        self.strategies: dict[str, typing.Union[TechnicalStrategy, BreakoutStrategy]] = {}

        self.logs = []

        self._ws_id = 1
        self._ws = None
        self._reconnect = 0
        
        t = threading.Thread(target=self._start_ws)
        t.start()


    def _start_ws(self):
        self._ws = websocket.WebSocketApp(self._wss_url, on_open=self._on_open, 
                                    on_message=self._on_message, on_close=self._on_close,
                                    on_error=self._on_error)
        
        while True and self._reconnect <= 5:
            try:
                self._ws.run_forever()
            except Exception as e:
                logger.error("Binance error in run_forever() method: %s", e)

            time.sleep(2)
            self._reconnect += 1


    def _on_message(self, ws, msg: str):
        data = json.loads(msg)
        
        # orderbook actualisation
        if data.get("e") == "bookTicker":
            self.prices.update({data['s']: {'bid': float(data['b']), 
                                            'ask': float(data['a'])}})
            
        elif data.get("e") == "aggTrade":
            
            for strat in self.strategies.values():
                if strat.contract.symbol == data['s']:
                    strat.parse_trade(float(data['p']), float(data['q']), data['T'])
                



            # loop through the strategies to find if the ticker is in strategies
             



            # if data['s'] == "BTCUSDT":
                # self._add_logs(f"{data['s']} bid: {data['b']} | ask: {data['a']}")

            # print(data['s'], "|", self.prices[data['s']])

        


    def _on_open(self, ws):
        logger.info("Binance connection opened")
        # self.subscribe_channel(self.contracts["BTCUSD"])
        self.subscribe_channels(list(self.contracts.values()), "bookTicker")
        self.subscribe_channels(list(self.contracts.values()), "aggTrade")


    def _on_close(self, ws):
        logger.warning("Binance connection closed")


    def _on_error(self, ws, msg: str):
        logger.error("Binace connection error: %s", msg)


    def subscribe_channel(self, contract: Contract):
        try: 
            self._ws.send(json.dumps({'symbol': contract.symbol, 'method': 'SUBSCRIBE',
                                 'id': self._ws_id, 'params': [contract.symbol.lower() + "@bookTicker"]}))
        
        except Exception as e:
            logger.error("Websocket error while subscribing to %s: %s", contract.symbol, e)
        
        self._ws_id += 1


    def subscribe_channels(self, contracts: list[Contract], channel: str):
        try: 
            self._ws.send(json.dumps({'method': 'SUBSCRIBE', 'id': self._ws_id,
                                       'params': [contract.symbol.lower() + "@" + channel
                                 for contract in contracts]}))
        
        except Exception as e:
            logger.error("Websocket error while subscribing to %s contracts on \
                         channel %s, error details: %s", len(contracts), channel, e)
        
        self._ws_id += 1

    def _generate_sig(self, data: dict) -> str:
        return hmac.new(self._secret_key.encode(), urlencode(data).encode(), 
                        hashlib.sha256).hexdigest()

    
    def _make_request(self, method: str, endpoint: str, data: dict):
        if method == "GET":
            try:
                response = requests.get(self._base_url + endpoint, params = data, 
                                    headers=self._headers)
            except Exception as e: 
                logger.error("Connection error while making %s request to %s endpoint: %s",
                             method, endpoint, e)
        elif method == "POST":
            try: 
                response = requests.post(self._base_url + endpoint, params = data, 
                                    headers=self._headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s endpoint: %s",
                             method, endpoint, e)
        elif method == "DELETE":
            try:
                response = requests.delete(self._base_url + endpoint, params = data, 
                                    headers=self._headers)
            except Exception as e:
                logger.error("Connection error while making %s request to %s endpoint: %s",
                             method, endpoint, e)
        else:
            raise ValueError()
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error("Error while making %s request to %s: returned %s (status code %s)",
                         method, endpoint, response.json(), response.status_code)
            return None


    def get_contracts(self) -> dict[str, Contract]:
        exchange_info = self._make_request("GET", "/fapi/v1/exchangeInfo", None)
        # return {cntr['pair']:cntr for cntr in exchange_info['symbols']} 
        return {cntr['symbol']: Contract(cntr, "bi") for cntr in exchange_info['symbols']}
    

    def get_historical_candles(self, contract: Contract, interval: str) -> list[Candle]:
        if raw_candles := self._make_request("GET", "/fapi/v1/klines", 
                        {'symbol': contract.symbol, 'interval': interval, 'limit': 1000}):
            # candles = [[c[0], float(c[1]), float(c[2]), float(c[3]), float(c[4]),
            #             float(c[5])] for c in raw_candles]
            return [Candle(c, "bi") for c in raw_candles]
    

    def get_bid_ask(self, contract: Contract) -> dict[str, float]:
        ob_data = self._make_request("GET", "/fapi/v1/ticker/bookTicker",
                                    {'symbol': contract.symbol})
        if ob_data:
            self.prices[contract.symbol] = {'bid': float(ob_data['bidPrice']),
                                   'ask': float(ob_data['askPrice'])}
            return self.prices[contract.symbol]
    

    def get_balances(self) -> dict[str, Balance]:
        data = {'timestamp': int(time.time() * 1000)}
        data['signature'] = self._generate_sig(data)
        if acc_data := self._make_request("GET", "/fapi/v1/account", data):
            return {a['asset']: Balance(a, "bi") for a in acc_data['assets']}
    
    
    def place_order(self, contract: Contract, side: str, quantity: float, 
                    order_type: str, price=None, tif=None) -> OrderStatus:
        data = {"symbol": contract.symbol, "side": side,
                "quantity": round(quantity / contract.lot_size) * contract.lot_size,
                "type": order_type, "timestamp": int(time.time() * 1000)}
        
        if price: 
            data['price'] = round(price / contract.tick_size) * contract.tick_size
        if tif:
            data["tif"] = tif
        
        data['signature'] = self._generate_sig(data)
        if order_status := self._make_request("POST", "/fapi/v1/order", data):
            return OrderStatus(order_status, "bi")
    
    
    def cancel_order(self, contract: Contract, orderId: int) -> OrderStatus:
        data = {'symbol': contract.symbol, 'orderId': orderId, 'timestamp': 
                int(time.time() * 1000)}
        data['signature'] = self._generate_sig(data)
        if order_status := self._make_request("DELETE", "/fapi/v1/order", data):
            return OrderStatus(order_status, "bi")


    def get_order_status(self, contract: Contract, order_id: int) -> OrderStatus:
        data = {'timestamp': int(time.time() * 1000), 'symbol': contract.symbol, 
                'orderId': order_id}
        data['signature'] = self._generate_sig(data)
        if order_status := self._make_request("GET", "/fapi/v1/order", data):
            return OrderStatus(order_status, "bi")
        
    
    def _add_logs(self, msg: str):
        logger.info("%s", msg)
        self.logs.append({'log': msg, 'displayed': False})



