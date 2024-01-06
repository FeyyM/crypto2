import logging
import requests
import pprint


logger = logging.getLogger()

def write_log():
    logger.info("Hello from Binance connector")


# "https://fapi.binance.com"
# "https://fapi.binance.com"

# "wss://fstream.binance.com"
    

def get_contracts():
    response_obj = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo")
    print(response_obj.status_code, response_obj.json())
    # pprint.pprint(response_obj.json())
    # file = open('justsymbols.txt', "w")
    # pprint.pprint(response_obj.json()["symbols"], file)
    # file.close()

    contracts = []
    for contract in response_obj.json()["symbols"]:
        # pprint.pprint(contract)
        print(contract['pair'])
        contracts.append(contract["pair"])

    return contracts


print(get_contracts())

