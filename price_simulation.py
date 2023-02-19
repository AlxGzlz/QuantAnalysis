#based on a post from PythonForFinance: https://www.pythonforfinance.net/2016/11/28/monte-carlo-simulation-in-python/
#calculate the volatility of the asset
histo_vol=qt.stats.volatility(df_returns)

#calculate the volatility forecast based on the GARCH model
def garch_vol(df):
    forecast = res.forecast(horizon=1, reindex=False)
    variance_forecast = forecast.variance.iloc[-1][0]
    # compute the annualized volatility forecast
    volatility_forecast = np.sqrt(variance_forecast)
    annualized_volatility_forecast = volatility_forecast * np.sqrt(252)/100
    return annualized_volatility_forecast

garch_vol=garch_vol(df_returns)

#price on the last recorded date
start_date=df_day['Close'][-1]
#number of trading days per year
T=365

#compute a Monte-Carlo simulation for the asset price
def price_simulation(histo_vol, cagr, start_date, T, daily_returns):
    result=[]
    for i in range(100000):
        daily_returns=np.random.normal(cagr/T,volatility/math.sqrt(T),T)+1
        price_list = [start_date]
        for x in daily_returns:
            price_list.append(price_list[-1]*x)
        result.append(price_list[-1])
        return price_list

result_histo = price_simulation(histo_vol, cagr, start_date, T, df_returns)
result_forecast=price_simulation(garch_vol, cagr, start_date, T, df_returns)

def stat_vol(df):
    q5 = np.percentile(df,5)
    q95 =np.percentile(df,95)
    median=np.median(df)
    return q5,q95,median

stat_vol_histo=stat_vol(result_histo)
stat_vol_forecast=stat_vol(result_forecast)

%matplotlib widget
figure, hist=plt.subplots(2,1, figsize=(15,15))
hist[0].set_title("Price prediction based on historic volatility "+t)
hist[0].set_ylabel("% probability")
hist[0].hist(result_histo, bins=100)
hist[0].axvline(stat_vol_histo[0],color='r', linestyle='dashed', linewidth=2)
hist[0].axvline(stat_vol_histo[1],color='r', linestyle='dashed', linewidth=2)
hist[0].axvline(stat_vol_histo[2],color='r', linestyle='dashed', linewidth=2)
hist[1].set_title("Price prediction based on forecast volatility "+t)
hist[1].set_ylabel("% probability")
hist[1].hist(result_forecast, bins=100)
hist[1].axvline(stat_vol_forecast[0],color='r', linestyle='dashed', linewidth=2)
hist[1].axvline(stat_vol_forecast[1],color='r', linestyle='dashed', linewidth=2)
hist[1].axvline(stat_vol_forecast[2],color='r', linestyle='dashed', linewidth=2)
plt.show()
