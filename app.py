# Importing essential libraries for parsing data and presentation
import streamlit as st
import numpy as np
import pandas as pd

# Importing scripts from individual oracles
import scripts.chainlink
import scripts.tellor
import scripts.dia
import scripts.band

# Configuration!
st.set_page_config(
     page_title="Oracle-Diff",
     page_icon="🔮",
     layout="centered",
     initial_sidebar_state="expanded",
)

"""
# Comparing Oracles
Written by: Christopher Pondoc

In order to dip my feet into the world of crypto and blockchain development, I decided to analyze different oracles
within the space and compare relevant metrics, enabling me to gain comprehension through practical data science work.

*Note: Streamlit data app may take a few seconds to load in data from Ethereum Mainnet!*
"""

"""
## Background
Oracles help bring data from the outside world onto the blockchain, which help smart contracts make decisions/dispense money/perform 
a plethora of tasks [1]. The data we'll be focusing on comes in the form on **conversion rates**, such as BTC/USD or BTC/ETH.

### Specific Oracles
In the case of this task, we'll be focusing on the following oracles:
* Tellor [2]
* Chainlink [3]
* Band Protocol [4]
* DIA [5]
"""

""" 
## Grabbing Data
The first step is to grab pertinent data from each of the oracles. In this case, I first decided 

### Conversion Rates
The first data I looked at were simply the pure conversion rates. For this, I simply pulled the data from each
of the smart contracts using their Application Binary Interface (ABI), as well as `web3.py`.

Specifically, I decided to key in on the following conversions:
* BTC/USD
* ETH/USD
* AMPL/USD
* LTC/USD

Below is a table of initial results. Note that for the Band Protocol, I had a bit of trouble communicating with their
smart contract to get the values for AMPL and LTC, so I marked those as `-1`.
"""

coins = ["BTC", "ETH", "AMPL", "LTC"] # Coins to look at!

# Dataframe for the Oracle
oracles = pd.DataFrame({
    'Name': [],
    'BTC/USD': [],
    'ETH/USD': [],
    'AMPL/USD': [],
    'LTC/USD': []
})

# Getting data for Chainlink
oracles.loc[len(oracles.index)] = ['Chainlink'] +  scripts.chainlink.grab_feeds()

# Getting data for Tellor
tellor_contract = scripts.tellor.set_up_contract()
oracles.loc[len(oracles.index)] = ['Tellor'] + scripts.tellor.grab_feeds(tellor_contract)

# Getting data for Dia
dia_data = ['DIA']
for i in range(0, len(coins)):
    dia_data.append(scripts.dia.return_price(coins[i]))
oracles.loc[len(oracles.index)] = dia_data

# Getting data for Band Protocol
band_contract = scripts.band.get_contract()
band_data = ['Band']
for i in range(0, len(coins) - 2):
    band_data.append(scripts.band.return_prices(band_contract, coins[i]))
oracles.loc[len(oracles.index)] = band_data + [-1, -1]

# Display data as a table
oracles

"""
### Change in Exchange Rate over Time
The next metric I decided to look at was the change in value over time of a certain exchange. Specifically,
I looked at the last 50 values of each exchange, and then compared over each exchange. See the line chart for
each exchange, as well as for each protocol, below.

Key:
* 0 - Tellor
* 1 - Chainlink
"""

"""
#### Note: Horizontal Axis is Request #, Vertical Axis is Price
"""

coin_prices = np.zeros((2, 51)) # To store data

# Loop for each protocol
for coin in coins:
    tellor_btc_prices = scripts.tellor.grab_price_change(tellor_contract, coin + "/USD")
    chainlink_btc_prices = scripts.chainlink.grab_price_change(coin + "/USD")
    coin_prices[0] = tellor_btc_prices
    coin_prices[1] = chainlink_btc_prices
    st.markdown('** Graph of Value of ' + coin + ' **')
    st.line_chart(np.transpose(coin_prices))

"""
### Average Time Between Each Request
Next, I decided to investigate the time that it took to satisfy each request. When looking at networks
like Tellor, due to the economics of the token, time between each request is not a pertinent 
"""

"""
#### Tellor
This graph takes a look at a couple of different requests for different conversions. The horizontal
axis represents request number while the vertical axis represents number of seconds.

Key:
* 0 - Tellor
* 1 - Chainlink

Average amount of time (in seconds): 
"""
    
coin_times = np.zeros((2, 50)) # To store data
averages = [0, 0] # To look at coin averages

# Looping through each coin
for i in range(0, len(coins)):

    # Grab time changes
    tellor_times = scripts.tellor.grab_time_change(tellor_contract, coins[i] + "/USD")
    chainlink_times = scripts.chainlink.grab_time_change(coins[i] + "/USD")

    # Update stacked array and avearges
    coin_times[0] = tellor_times
    coin_times[1] = chainlink_times
    averages[0] = np.average(tellor_times)
    averages[1] = np.average(chainlink_times)

    # Print out values for specific coin
    st.markdown('** Graph of time in between requests of ' + coins[i] + ' **')
    st.text('Average time in between each request for Tellor: ' + str(averages[0]) + ' seconds')
    st.text('Average time in between each request for Chainlink: ' + str(averages[1]) + ' seconds')
    st.line_chart(np.transpose(coin_times))

"""
### Gas Prices
The final metric I decided to investigate involved analyzing the gas estimates for calling certain functions
from each oracle's smart contract. Specifically, I focused on looking at the amount of gas required to pull a specific
value from the chain, as well as how that value changed for each exchange.

Key:
* 0 - Tellor
* 1 - Chainlink
"""

# Grabbing all gas prices
gas_prices = []
gas_prices.append(scripts.tellor.grab_gas_estimate(tellor_contract, "BTC/USD"))
gas_prices.append(scripts.chainlink.grab_gas_estimate("BTC/USD"))
st.markdown("** Graph of Gas Estimates for Grabbing Current Value **")
st.text('Average Gas Price for Single Value Request for Tellor: ' + str(gas_prices[0]) + ' Gwei')
st.text('Average Gas Price for Single Value Request for Chainlink: ' + str(gas_prices[1]) + ' Gwei')
st.bar_chart((gas_prices))

"""
## Works Cited
[1] https://www.coindesk.com/what-is-an-oracle

[2] https://tellor.io/

[3] https://chain.link/

[4] https://bandprotocol.com/

[5] https://diadata.org/
"""