"""
File: tellor.py
Grabs data from Tellor and get all results
"""

""" Necessary Libraries """
import json
from web3 import Web3

""" Constants """
granularity = 1000000 # Defined granularity for all of the data feeds

"""
Function: set_up_contract()
Accesses the Tellor ABI, connects to the Tellor contract, and returns to use
"""
def set_up_contract():
    f = open('contracts/tellorLens.json',)
    abi = json.load(f)
    web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/f5470eb326af43adadbb81276c2e4675'))
    address = '0xb2b6c6232d38fae21656703cac5a74e5314741d4'
    f.close()
    return web3.eth.contract(address=Web3.toChecksumAddress(address), abi=abi)

""" 
Function: grab_feeds()
Get the correct data feed IDs from Tellor and get their value
"""
def grab_feeds(contract):
    prices = []
    with open('feeds/tellor.json') as f:
        data = json.load(f)
    for elem in data:
        id_num = int(data[elem]['id'])
        [worked, value, timestamp] = (contract.functions.getCurrentValue(id_num).call())
        prices.append(value/granularity)
        for i in range(0, 50):
            [worked, value, timestamp] = (contract.functions.getDataBefore(id_num, timestamp).call())
    return prices

"""
Function: grab_price_change()
Get the change in price over a certain amount of time!
"""
def grab_price_change(contract, id_name):
    all_prices = []
    with open('feeds/tellor.json') as f:
        data = json.load(f)
    id_num = int(data[id_name]['id'])
    [worked, value, timestamp] = (contract.functions.getCurrentValue(id_num).call())
    all_prices.append(value/granularity)
    for i in range(0, 50):
        [worked, value, timestamp] = (contract.functions.getDataBefore(id_num, timestamp).call())
        all_prices.append(value/granularity)
    return all_prices[::-1]


"""
Function: print_data()
Print all of the data!
"""
def print_data(elem, value, timestamp):
    print("Tellor Data for " + str(elem))
    print("Exchange Rate: " + str(value/granularity))
    print("Timestamp: " + str(timestamp))
    print("\n")

""" 
Function: main
Runs all of the entirety of the helper functions
"""
if __name__ == "__main__":
    contract = set_up_contract()
    grab_feeds(contract)
    grab_price_change(contract, "BTC/USD")
    