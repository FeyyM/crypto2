import logging

import requests
import pprint


def get_contracts():

    response_object = requests.get("https://www.bitmex.com/api/v1/instrument/active")

    return [contract['symbol'] for contract in response_object.json()]


pprint.pprint(get_contracts())
