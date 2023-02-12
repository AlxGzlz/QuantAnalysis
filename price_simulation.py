#based on a post from PythonForFinance: https://www.pythonforfinance.net/2016/11/28/monte-carlo-simulation-in-python/
#calculate the volatility of the asset
volatility=qt.stats.volatility(df_returns)

#price on the last recorded date
start_date=df_day['Close'][-1]
#number of trading days per year
T=365
#define result array 
result=[]

#compute a defined number of simulations on the possible price evolution
for i in range(10000):
    daily_returns=np.random.normal(cagr/T,volatility/math.sqrt(T),T)+1
    price_list = [start_date]
    for x in daily_returns:
        price_list.append(price_list[-1]*x)
    result.append(price_list[-1])
    
quantile5 = np.percentile(result,5)
quantile95 =np.percentile(result,95)

%matplotlib widget
plt.hist(result,bins=100)
plt.axvline((quantile5), color='r', linestyle='dashed', linewidth=2)
plt.axvline((quantile95), color='r', linestyle='dashed', linewidth=2)
plt.show()
