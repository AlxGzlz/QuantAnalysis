#calculate the average price of the loaded time period
average_price = float(np.mean(df_day['close']))
average_price = round(average_price, 2)
#integrate the average price in the dataframe of the loaded instrument
df_day['average price'] = average_price
#calculate the average return of the loaded time period
average_return = float(average_return)*100
average_return = round(average_return, 4)
#calculate the Simple Moving Average (sma)
sma = pta.sma(df_day["close"])
#calculate the Exponential Moving Average
ema = pta.ema(df_day["close"])

%matplotlib widget
plt.title("Daily prices evolution of "+ ticker[0])
plt.plot(df_day['close'], label="price", c="blue")
plt.plot(df_day['average price'], label="avg price", c="red")
plt.plot(sma, label ="SMA", c="green")
plt.plot(ema, label = "EMA", c="yellow")
plt.xlabel("datetime")
plt.ylabel("price in $")
plt.legend()
plt.show()
print("The average price on the loaded period is: $", average_price)
