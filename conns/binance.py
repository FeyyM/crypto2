import logging
import requests
import time
from urllib.parse import urlencode


import hmac
import hashlib



logger = logging.getLogger()




class BinClient:
    def __init__(self, public_key, secret_key, testnet = True) -> None:

        self.public_key = public_key
        self.secret_key = secret_key
        self.base_url = "https://testnet.binancefuture.com" if testnet else "https://fapi.binance.com"
        self.headers = {"X-MBX-APIKEY": public_key}


        logger.info("Binance Futures Client successfully initialized")

        self.strategies = dict()

    def _make_request(self, method, endpoint, data = None):

        if method == "GET":
            resp = requests.get(self.base_url + endpoint, params = data,
                                headers=self.headers)
        elif method == "POST":
            pass
        elif method == "DELETE":
            pass
        else:
            raise ValueError()
        
        if resp.status_code == 200:
            return resp.json()
        else:
            logger.error("Error while making %s request to %s: %s (error code %s)", method,
                         endpoint, resp.json(), resp.status_code)

    def _gen_sig(self, data):
        return hmac.new(self.secret_key.encode(), urlencode(data).encode(),
                        hashlib.sha256).hexdigest()
    
    def get_historical_candles(self, symbol, interval):
        data = {'symbol': symbol, 'interval': interval, 'limit': 1000}
        raw_candles = self._make_request("GET", "/fapi/v1/klines", data)
        return [(c[0], float(c[1]), float(c[2]), float(c[3]), float(c[4]), 
                float(c[5])) for c in raw_candles]


    def get_bid_ask(self, symbol):
        
        data = {'symbol': symbol}
        ob_data = self._make_request("GET", "/fapi/v1/ticker/bookTicker", data)
        
        if ob_data:
            self.prices.update({symbol: {'bid': float(ob_data['bidPrice']),
                                     'ask': float(ob_data['askPrice'])}})
        
        return self.prices[symbol]


    def get_contracts(self):
        # logger.info("wirte from binance")
        endpoint = "/fapi/v1/exchangeInfo"
        ex_info = self._make_request("GET", endpoint)
        contracts = dict()
        if ex_info:
            for contract in ex_info["symbols"]:
                contracts[contract["pair"]] = contract
        return contracts
    

    def get_balances(self):
    
        data = {'timestamp': int(time.time() * 1000)}
        data['signature'] = self._gen_sig(data)

        acc = self._make_request("GET", "/fapi/v1/account", data)

        return {a['asset']: a for a in acc['assets']} if acc else dict()

    def get_order_status(self, symbol, order_id):
        
        data = {'timestamp': int(time.time()*1000), 'symbol': symbol,
                'orderId': order_id}
        data['signature'] = self._gen_sig(data)
        return self._make_request("GET", "/fapi/v1/order", data)
        
     

    def place_order(self, symbol, side, quantity, ord_type, price=None, tif=None):
        data = {'symbol': symbol, 'side':side, 'quantity': quantity,
                'type': ord_type, 'timestamp': int(time.time()*1000)}
        if price:
            data['price'] = price
        if tif:
            data['timeINForceprice'] = tif
        data['signature'] = self._gen_sig(data)
        return self._make_request("POST", '/fapi/v1/order', data)


    def cancel_order(self, symbol, order_id):
        
        data = {'orderId': order_id, 'symbol': symbol, 'timestamp':
                int(time.time()*1000)}
        data['signature'] = self._gen_sig(data)
        
        return self._make_request("DELETE", "/fapi/v1/order", data)
    


# print(get_contracts())