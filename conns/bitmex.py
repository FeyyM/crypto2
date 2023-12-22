import requests



def get_contracts():


    resp_obj = requests.get("https://www.bitmex.com/api/v1/instrument/active")

    return [cnc["symbol"] for cnc in resp_obj.json()]



print(get_contracts())


