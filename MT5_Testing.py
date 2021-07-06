import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot
plot.style.use('fivethirtyeight')
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pytz
from pyti.relative_strength_index import relative_strength_index as rsi

#pd.set_option("display.max_rows", None, "display.max_columns", None) #Shows max dataframe
# display data on the MetaTrader 5 package
print("MetaTrader5 package author: ",mt5.__author__)
print("MetaTrader5 package version: ",mt5.__version__)
 
# establish MetaTrader 5 connection to a specified trading account
if not mt5.initialize(login=***, server="BDSwissGlobal-Server01",password="***"):
    print("initialize() failed, error code =",mt5.last_error())
    quit()
 
# display data on connection status, server name and trading account
print(mt5.terminal_info())
# display data on MetaTrader 5 version
print(mt5.version())

# prepare the buy request structure
lotsize = 0.01
symbol = "BTCUSD"
symbol_info = mt5.symbol_info(symbol)
if symbol_info is None:
    print(symbol, "not found, can not call order_check()")
    mt5.shutdown()
    quit()
# if the symbol is unavailable in MarketWatch, add it
if not symbol_info.visible:
    print(symbol, "is not visible, trying to switch on")
    if not mt5.symbol_select(symbol,True):
        print("symbol_select({}}) failed, exit",symbol)
        mt5.shutdown()
        quit()

# #now = datetime.now() # current date and time

# year = now.strftime("%Y")
# print("year:", year)
# year = int (year)
# month = now.strftime("%m")
# print("month:", month)
# month = int (month)
# day = now.strftime("%d")
# print("day:", day)
# day = int (day)

# # set time zone to UTC
timezone = pytz.timezone("Etc/UTC")
# create 'datetime' object in UTC time zone to avoid the implementation of a local time zone offset



gmt_from = datetime.now() + timedelta(hours=2) - timedelta(minutes=1)
utc_from = datetime(2020, 1, 10, tzinfo=timezone)
utc_to = datetime(2020, 1, 12, tzinfo=timezone)
rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M1, gmt_from, 20000)

# display each element of obtained data in a new line
# print("Display obtained data 'as is'")
# for rate in rates:
#     print(rate)
 
# create DataFrame out of the obtained data
pastdata = pd.DataFrame(rates)
# convert time in seconds into the datetime format
pastdata['time']=pd.to_datetime(pastdata['time'], unit='s')
pastdata = pastdata.set_index(pastdata['time'].values)
pastdata = pastdata.drop(columns=['time', 'open', 'high', 'low', 'tick_volume', 'spread', 'real_volume'])


hourlyrates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_H1, gmt_from, 334)

hourlypastdata = pd.DataFrame(hourlyrates)
hourlypastdata['time'] = pd.to_datetime(hourlypastdata['time'], unit='s')

iRSI = pd.DataFrame(rsi(hourlypastdata['close'], 14))
hourlytime = hourlypastdata['time']

HourlyRSI = pd.concat([hourlytime, iRSI], axis = 1)



#iRSIdf = pd.DataFrame(iRSI)
# print ('RSI TABLE')
# print (iRSIdf)
# iRSI_NOW = iRSIdf.iat[498,0]
# print ('RSI Now')
# print (iRSI_NOW)

# display data
print("\nDisplay dataframe with data")
print(pastdata) 
period = 20
pastdata['SMA'] = pastdata['close'].rolling(window=period).mean()
#pastdata['50SMA'] = pastdata['close'].rolling(window=50).mean()
pastdata['200SMA'] = pastdata['close'].rolling(window=200).mean()
pastdata['200SMA+'] = pastdata['200SMA'] + (0.0025 * 300000)
pastdata['200SMA-'] = pastdata['200SMA'] - (0.0025 * 300000)
pastdata['SLTop'] = pastdata['200SMA'] + (0.003 * 300000)
pastdata['SLBot'] = pastdata['200SMA'] - (0.003 * 300000)
pastdata['STD'] = pastdata['close'].rolling(window=period).std()
pastdata['Upper'] = pastdata['SMA'] + (pastdata['STD'] * 2.5)
pastdata['Lower'] = pastdata['SMA'] - (pastdata['STD'] * 2.5)
column_list = ['close', 'SMA', '200SMA', 'Upper', 'Lower']



df = pastdata[199:]
print(df)
x = 8
def get_signal(data):

	close_buy = []
	close_sell = []
	buy_signal = []
	sell_signal = []

	for i in range(len(data['close'])):
		if ((data['close'][i] > data['Upper'][i]) & (x == 8) & (data['close'][i] > (data['200SMA'][i] + (0.0015 * 275000)))):
			close_buy.append(data['close'][i])
			close_sell.append(np.nan)
			buy_signal.append(np.nan)
			sell_signal.append(np.nan)
			print(str(data.index[i]) + ', Close Buy at, , ,' + str(data['close'][i]))
		elif ((data['close'][i] < data['Lower'][i]) & (x == 8) & (data['close'][i] < (data['200SMA'][i] - (0.0015 * 275000)))):
			close_buy.append(np.nan)
			close_sell.append(data['close'][i])
			buy_signal.append(np.nan)
			sell_signal.append(np.nan)
			print(str(data.index[i]) + ', Close Sell at, , , ,' + str(data['close'][i]))
		elif (data['close'][i] > data['Upper'][i]) & (data['200SMA-'][i] < data['close'][i] < data['200SMA+'][i]) & (data['close'][i] > data['200SMA'][i]) & ((data['200SMA'][i-15] - data['200SMA'][i]) > -(0.0001 * 100000)):# & (data['SMA'][i] > data['200SMA'][i]):
			close_buy.append(np.nan)
			close_sell.append(np.nan)
			buy_signal.append(np.nan)
			sell_signal.append(data['close'][i])
			print(str(data.index[i]) + ', Sell at,' + str(data['close'][i]))
		elif (data['close'][i] < data['Lower'][i]) & (data['200SMA-'][i] < data['close'][i] < data['200SMA+'][i]) & (data['close'][i] < data['200SMA'][i]) & ((data['200SMA'][i] - data['200SMA'][i-15]) > -(0.0001 * 100000)):# & (data['SMA'][i] < data['200SMA'][i]):
			close_buy.append(np.nan)
			close_sell.append(np.nan)
			buy_signal.append(data['close'][i])
			sell_signal.append(np.nan)
			print(str(data.index[i]) + ', Buy at, ,' + str(data['close'][i]))
		else:
			close_buy.append(np.nan)
			close_sell.append(np.nan)
			buy_signal.append(np.nan)
			sell_signal.append(np.nan)
	return (close_buy, close_sell, buy_signal, sell_signal)

df['Close_Buy'] = get_signal(df)[0]
df['Close_Sell'] = get_signal(df)[1]
df['Buy'] = get_signal(df)[2]
df['Sell'] = get_signal(df)[3]

print (df)
fig = plot.figure(figsize=(12.2,6.4))
ax = fig.add_subplot(1,1,1)
x_axis = df.index
ax.fill_between(x_axis, df['Upper'], df['Lower'], color = 'grey')
ax.plot(x_axis, df['close'], color = 'gold', lw = 1, label = 'Close Price')
ax.plot(x_axis, df['SMA'], color = 'blue', lw = 1, label = 'Simple Moving Average')
#ax.plot(x_axis, df['50SMA'], color = 'orange', lw = 2, label = '50 Simple Moving Average')
ax.plot(x_axis, df['200SMA'], color = 'black', lw = 2, label = '200 Simple Moving Average')
ax.plot(x_axis, df['200SMA+'], color = 'black', lw = 2, label = '200+ SMA')
ax.plot(x_axis, df['200SMA-'], color = 'black', lw = 2, label = '200- SMA')
ax.plot(x_axis, df['SLTop'], color = 'Red', linestyle = 'dashed', lw = 2, label = 'SLTop')
ax.plot(x_axis, df['SLBot'], color = 'Red', linestyle = 'dashed', lw = 2, label = 'SLBot')
ax.scatter(x_axis, df['Close_Buy'], color = 'blue', lw = 2, label = 'Close_Buy', marker = '<')
ax.scatter(x_axis, df['Close_Sell'], color = 'orange', lw = 2, label = 'Close_Sell', marker = '>')
ax.scatter(x_axis, df['Buy'], color = 'green', lw = 2, label = 'Buy', marker = '^')
ax.scatter(x_axis, df['Sell'], color = 'Red', lw = 2, label = 'Sell', marker = 'v')
ax.set_title('Bollinger Band for ' + str(symbol))
ax.set_xlabel('DateTime')
ax.set_ylabel(str(symbol))
ax.legend()

pd.set_option("display.max_rows", None, "display.max_columns", None) #Shows max dataframe
print (HourlyRSI)

plot.show()


#shut down connection to the MetaTrader 5 terminal
mt5.shutdown()
