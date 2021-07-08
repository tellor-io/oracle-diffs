# Importing essential libraries for parsing data and presentation
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import streamlit as st

# Importing scripts from individual oracles
import scripts.chainlink
import scripts.tellor
import scripts.dia
import scripts.band
import scripts.gas

# Streamlit Configuration!
st.set_page_config(
     page_title="Oracle-Diff",
     page_icon="🔮",
     layout="centered",
     initial_sidebar_state="expanded",
)

# Matplotlib Configuration!
fe = fm.FontEntry(
    fname='style/Renogare.ttf',
    name='Renogare')
fm.fontManager.ttflist.insert(0, fe)
mpl.rcParams['font.family'] = fe.name
mpl.rcParams['xtick.labelsize'] = 8

"""
# 🔮 Comparing Oracles
👨🏽‍💻 Written by: [Christopher Pondoc](http://chrispondoc.com/)

This project analyzes different oracles within the world of blockchain development through a data science lens.
By observing and comparing various relevant metrics of oracles, I was able to gain some reasonable comprehension about
the world of crypto more practically.

*Note: Streamlit data app may take a few seconds to load in data from Ethereum Mainnet!*
"""

"""
***
## 📚 **Background**
Developing on the blockchain starts with smart contracts, which are self-operating computer programs, which live on the blockchain and execute
when a certain amount of conditions are met [1]. Despite the many advantages of smart contracts, one limiting factor is the inability to get data from
outside of the blockchain onto the blockchain. Such data can include information about the weather, random numbers, or price feeds of different currencies.

This is where oracles come in: these mechanisms help to retrieve data from off the blockchain for smart contracts to use for dispensing money, making decisions,
and more [2]. In this specific report, we'll be looking at oracles and price feed data, and understanding how different oracles perform compared to one another.

### **Specific Oracles**
In the case of this task, we'll be focusing on the following oracles. As a primer to the differences between the differences between these oracles and their
implementations, check out this [article](https://www.reddit.com/r/TellorOfficial/comments/nv2ej1/oracle_comparison_what_makes_tellor_different/?utm_medium=android_app&utm_source=share):
* Tellor [3]
* Chainlink [4]
* Band Protocol [5]
* DIA [6]
"""

""" 
***
## 💻  **Process**
The first step is to grab pertinent data from each of the oracles. In this case, I followed a specific process:


1. First, I found the address of each oracle's smart contract on the blockchain. For the most part, all the oracles provided
the address to their smart contract through the documentation on their website.

2. After finding the addresses of each smart contract, I went to EtherScan, and downloaded each contract's Application Binary
Interface, or ABI [7]. Since smart contracts are stored and compiled in the blockchain as bytecode, in order to communicate with a smart
contract, we must use an ABI to determine which functions I can invoke as well as what format data will be returned to me [8].

3. Finally, using `web3.py`, I was able to connect each of the project's smart contract, invoke the proper arguments, and then calculate
the metrics accordingly [9].

Below is a code sample that can be used as a template for connecting to a smart contract using `web3.py`. More code samples can be found
in the `scripts` folder in the main repository [10]:

```
from web3 import Web3
import json

f = open('path/to/abi', 'r')
abi = json.load(f)
web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/PROJECT_URL'))
address = 'CONTRACT_ADDRESS'
f.close()
return web3.eth.contract(address=address, abi=abi)
```

"""

# Getting proper gas times and stuff
chainlink_times, chainlink_timestamps = scripts.chainlink.grab_time_change("BTC/USD")
gas_prices, gas_times = scripts.gas.get_timestamps()
indices = []
for timestamp in chainlink_timestamps:
    difference = int(10000000)
    index = int(0)
    for other_timestamp in gas_times:
        other_diff = int(abs(other_timestamp - int(datetime.timestamp(timestamp))))
        print(other_diff)
        if (other_diff < difference):
            difference = other_diff
            index = int(gas_times.index(other_timestamp))
    indices.append(index)
indices
    

"""
***
## 📊 **Data Analysis**
### 💵 **Price Feeds**
The first data I looked at were simply the pure price feeds, mainly focusing on conversions between certain large cryptocurrencies.

Specifically, I decided to key in on the following conversions:
* BTC/USD
* ETH/USD
* AMPL/USD

For each oracle, I utilizes the below functions from their ABIs:
* Tellor: `getCurrentValue(uint256 _requestId)`
* Chainlink: `latestRoundData()`
* Band Protocol: `getReferenceData(string _base, string _quote)`
* DIA: `getCoinInfo(string name)`

Below is a table of initial results. Note that for the Band Protocol, I had a bit of trouble communicating with their
smart contract to get the values for AMPL, so I marked it as `-1`.
"""
# Coins, oracles, and timespans to look at!
coins = ["BTC", "ETH", "AMPL"]
oracle_names = ["Tellor", "Chainlink", "Band Protocol", "DIA"]
timespans = [25, 25, 8] # If changed, originally 80

# Dataframe for the Oracle
oracles = pd.DataFrame({
    'Name': [],
    'BTC/USD': [],
    'ETH/USD': [],
    'AMPL/USD': [],
})

# Getting data for Chainlink
oracles.loc[len(oracles.index)] = ['Chainlink'] +  scripts.chainlink.grab_feeds()

# Getting data for Tellor
tellor_contract = scripts.tellor.set_up_contract()
oracles.loc[len(oracles.index)] = ['Tellor'] + scripts.tellor.grab_feeds()

# Getting data for Dia
dia_data = ['DIA']
for i in range(0, len(coins)):
    dia_data.append(scripts.dia.return_price(coins[i]))
oracles.loc[len(oracles.index)] = dia_data

# Getting data for Band Protocol
band_data = ['Band']
for i in range(0, len(coins) - 1):
    band_data.append(scripts.band.return_prices(coins[i]))
oracles.loc[len(oracles.index)] = band_data + [-1]

# Display data as a table
st.table(oracles)

"""
***
### 🏷 **Change in Price Feed over Time**
The next metric I decided to look at was the change in value over time of a certain cryptocurrency. Due to the limitations
of specific oracles and their smart contracts, I was able to grab historical data from only Tellor and Chainlink.

As a general methodology, I first grabbed the latest request for a value for each price feed. For both Tellor and Chainlink,
the respective functions from the respective ABIs returned round IDs. Thus, by subtracting 1 for each previous round, I was able
to iterate over the previous 5 days by grabbing the value of a price feed at a specific ID or timestamp.

Below are the functions I utilized from each ABI:
* Tellor: `getDataBefore(uint256 _requestId, uint256 _timestamp)`
* Chainlink: `getRoundData(uint80 _roundId)`

*Note: Horizontal Axis is Request #, Vertical Axis is Price in USD*

"""

# Looking at all of the data, and then getting those values
for i in range(0, len(coins)):

    # Grab values
    tellor_prices, tellor_timestamps = scripts.tellor.get_better_price(coins[i] + "/USD", timespans[i])
    chainlink_prices = scripts.chainlink.get_better_price(coins[i] + "/USD", timespans[i])

    # Graph the values
    st.markdown('** Graph of Value of ' + coins[i] + '/USD **')
    fig, ax = plt.subplots()
    ax.plot(tellor_timestamps, tellor_prices, label="Tellor")
    ax.plot(tellor_timestamps, chainlink_prices, label="Chainlink")
    ax.set_title("Prices for " + coins[i] + "/USD", fontweight="bold", fontsize="10")
    ax.set_xlabel("Time", fontsize="10")
    ax.set_ylabel("Price (in USD)", fontsize="10")
    ax.set_xticks(tellor_timestamps[::5])
    ax.legend()
    st.pyplot(fig)

"""
***
### ⏱ **Average Time Between Each Request**
Next, I decided to investigate the time that it took to satisfy each request for the updated value of a price
feed. Between requests, I would calculate the time difference between the Unix timestamps of when the value was previously
updated to when the next requested was started.

*Note: Horizontal Axis is Request #, Vertical Axis is Time in Seconds*
"""

# Arrays for two important times to be analyzed
tellor_btc_times = []
chainlink_btc_times = []    
coin_times = np.zeros((2, 50)) # To store data
averages = [0, 0] # To look at coin averages

# Looping through each coin
for i in range(0, len(coins)):

    # Grab time changes
    tellor_times = scripts.tellor.grab_time_change(str(coins[i] + "/USD"))
    chainlink_times, chainlink_timestamps = scripts.chainlink.grab_time_change(coins[i] + "/USD")

    # Save BTC times for future reference
    if (i  == 0):
        tellor_btc_times = tellor_times
        chainlink_btc_times = chainlink_times

    averages[0] = np.average(tellor_times)
    averages[1] = np.average(chainlink_times)

    # Print out values for specific coin
    st.markdown('** Graph of time in between requests of ' + coins[i] + ' **')
    st.text('Average time in between each request for Tellor: ' + str(averages[0]) + ' seconds')
    st.text('Average time in between each request for Chainlink: ' + str(averages[1]) + ' seconds')

    # Graph values
    fig, ax = plt.subplots()
    ax.plot(chainlink_timestamps, tellor_times, label="Tellor")
    ax.plot(chainlink_timestamps, chainlink_times, label="Chainlink")
    ax.set_title("Time Between Each Request for " + coins[i] + "/USD", fontweight="bold", fontsize="10")
    ax.set_xlabel("Time", fontsize="10")
    ax.set_ylabel("Total Time to Fulfill Request (s)", fontsize="10")
    if (i != 2):
        axes = plt.gca()
        formatter = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")
        axes.xaxis.set_major_formatter(formatter)
        locator = mdates.DayLocator()
        axes.xaxis.set_major_locator(locator)
    ax.legend()
    st.pyplot(fig)

"""
***
### 📈 **Histogram of Time**
Note that due the economics of tokens like Tellor, looking at absolute speed is not the most important metric. If anything, a lack of erraticness + a commitment to 
consistency is much more consequential. Thus, in addition to looking at time per request over time + averages, one could also plot the distribution as a histogram
and analyze the standard deviation.
"""

# Histogram + Standard Deviation for Tellor
"""
#### Tellor
"""
st.text("Standard Deviation of Tellor times: " + str(np.std(tellor_btc_times)) + " seconds")
tellor_btc_histogram = np.histogram(tellor_btc_times, bins=15)[0]
st.bar_chart(tellor_btc_histogram)

# Histogram + Standard Deviation for Chainlink
"""
#### Chainlink
"""
st.text("Standard Deviation of Chainlink times: " + str(np.std(chainlink_btc_times)) + " seconds")
chainlink_btc_histogram = np.histogram(chainlink_btc_times, bins=15)[0]
st.bar_chart(chainlink_btc_histogram)

"""
***
### ⛽️ **Gas Prices**
The final metric I decided to investigate involved analyzing the gas estimates for retrieving data from each specific oracle.
Simply put, gas refers to the cost needed in order to perform a transaction on a blockchain network. Transactions fees are
equal to the product of the units of gas used and the price per unit. However, the units of gas is ultimately fixed [11]. In order
to calculate each gas price, I utilized the `estimate_gas()` function within `web3.py`.

It's also important to note that the amount of gas required is also highly dependent on the amount of data being sent back
from the smart contract and the function being called.

Key:
* 0 - Tellor
* 1 - Chainlink
* 2 - DIA
* 3 - Band Protocol
"""

# Grabbing all gas prices for calling BTC!
gas_prices = []
gas_prices.append(scripts.tellor.grab_gas_estimate("BTC/USD"))
gas_prices.append(scripts.chainlink.grab_gas_estimate("BTC/USD"))
gas_prices.append(scripts.dia.grab_gas_estimate("Bitcoin"))
gas_prices.append(scripts.band.grab_gas_estimate("BTC"))
st.markdown("** Graph of Gas Estimates for Grabbing Current Value **")

# Print all results!
for i in range(0, len(oracles)):
    st.text('Average Gas Price for Single Value Request for ' + oracle_names[i] + ': ' + str(gas_prices[i]) + ' Gwei')
st.bar_chart((gas_prices))

"""
***
## Works Cited
[1] https://medium.com/@teexofficial/what-are-oracles-smart-contracts-the-oracle-problem-911f16821b53

[2] https://www.coindesk.com/what-is-an-oracle

[3] https://tellor.io/

[4] https://chain.link/

[5] https://bandprotocol.com/

[6] https://diadata.org/

[7] https://etherscan.io/

[8] https://www.youtube.com/watch?v=F_l4HycnHAI&t=42s

[9] https://web3py.readthedocs.io/en/stable/index.html

[10] https://github.com/cpondoc/oracle-diff

[11] https://www.investopedia.com/terms/g/gas-ethereum.asp
"""