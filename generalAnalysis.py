#calculate the average price of the loaded time period
average_price = float(np.mean(df_day['Close']))
average_price = round(average_price, 2)
#integrate the average price in the dataframe of the loaded instrument
df_day['average price'] = average_price
#calculate the Simple Moving Average (sma)
sma = pta.sma(df_day["Close"])
#calculate the Exponential Moving Average
ema = pta.ema(df_day["Close"])

#based on the PQN025 Newsletter (https://pyquantnews.com/kalman-filter-openbb-for-parameterless-indicators/)
#computation of the Kalman Ratio for the closing prices of the asset
#define the parameter to compute the Kalman ratio
kf = KalmanFilter(
    transition_matrices = [1],
    observation_matrices = [1],
    initial_state_mean = 0,
    initial_state_covariance = 1,
    observation_covariance=1,
    transition_covariance=0.01)

#compute the Kalman ratio for the asset price*
def compute_Kalman(a):
    state_means, _ = kf.filter(a)
    state_means = pd.Series(state_means.flatten(), index=a.index)
    return state_means

#define a dedicated DataFrame for the YTD data
def calculate_ytd_returns(a):
    jan_1st_year = datetime(datetime.now().year, 1, 1)
    ytd = a.loc[a.index >= jan_1st_year]
    return ytd

#compute the average return of the asset over the defined time period  
def calculate_av_return(a):
    b=qt.stats.compsum(a)*100
    c=b.tail(1)
    c=float(c['Close'])
    return c

#compute the YTD return of the asset & the benchmark
df_ytd = calculate_ytd_returns(df_returns)
df_ytd_return=calculate_av_return(df_ytd)
bench_ytd = calculate_ytd_returns(bench_returns)
bench_ytd_return=calculate_av_return(bench_ytd)

#compute the returns for the other defined time periods
#if the defined time period is shorter than one of the define period below, the result will be equal for both of them
#ex: for a selection of 300 days, df_2y_return = df_return, even if it is not the case
df_6m_return = calculate_av_return(df_returns.tail(125))
df_1y_return = calculate_av_return(df_returns.tail(259))
df_2y_return = calculate_av_return(df_returns.tail(519))
df_return = calculate_av_return(df_returns)
bench_6m_return = calculate_av_return(bench_returns.tail(125))
bench_1y_return = calculate_av_return(bench_returns.tail(259))
bench_2y_return = calculate_av_return(bench_returns.tail(519))
bench_return = calculate_av_return(bench_returns)

#adjust the format of the indicators data
cagr = float(risk_analysis['cagr'])
cagr =  round(cagr,5)
treynor_ratio = float(risk_analysis['treynor ratio'])
treynor_ratio = round(treynor_ratio,5)

#compare the asset cagr with the benchmark's return 
def return_comparison(a,b):
    c = (a*100)-b
    c = round(c,3)
    return c

diff_benchmark = return_comparison(cagr, bench_return)


#compute the compounded total return over the loaded period
def compound_return(a):
    cpd = qt.stats.compsum(a)
    return cpd

#calculate the compounded returns for the loaded asset and the benchmark
cpd_return = compound_return(df_returns)
bench_cpd_return = compound_return(bench_returns)

#compute the rolling volatility of returns over the period
def rolling_volatility(returns, period):
    rolling_volatility = qt.stats.rolling_volatility(returns, period)
    return rolling_volatility

df_rolling_vol = rolling_volatility(df_returns, days)
bench_rolling_vol = rolling_volatility(bench_returns, days)

#compute the RSI & RSX indicators
df_day['rsx'] = pta.rsx(df_day['Close'].tail(90), length=14, drift=1, offset=0)
df_day['rsi'] = pta.rsi(df_day['Close'].tail(90), length=14, drift=1, offset=0)
bench_day['rsi'] = pta.rsi(bench_day['Close'].tail(90), length=14, drift=1, offset=0)

#plot the results
%matplotlib widget
figure, axis = plt.subplots(2,1, figsize=(15,15))
#plot the price & Kalman price of the asset
axis[0].set_title("Daily evolution of price of"+t)
axis[0].set_ylabel("price in $")
axis[0].plot(df_day['Close'], label="price", c="blue")
axis[0].plot(Kalman_df, label='Kalman', c="orange")
axis[0].plot(df_day['average price'], label="avg price over the period", c="red")
axis[0].legend(loc="upper right")
#plot the compounded returns of the asset and the benchmark
axis[1].set_title("Compounded returns over the period")
axis[1].set_ylabel("% return")
axis[1].plot(cpd_return,label=t,c="blue")
axis[1].plot(bench_cpd_return, label=b,c="orange")
axis[1].legend(loc='upper right')

figure, axis = plt.subplots(2,1, figsize=(15,15))
#plot the volatility of the asset
axis[0].set_title("Rolling volatility over the period")
axis[0].set_ylabel("Volatility ratio")
axis[0].plot(df_rolling_vol,label=t)
axis[0].plot(bench_rolling_vol,label=b)
axis[0].legend(loc='upper right')
#plot the RSI & RSX of the asset
axis[1].set_title("RSI & RSX evolution")
axis[1].plot(df_day['rsx'],label ='RSX', color='r')
axis[1].plot(df_day['rsi'],label ='RSI', color='b')
axis[1].plot(bench_day['rsi'],label='bench RSI',color='g')
axis[1].legend(loc='upper right')
print("")
print("Over the period:")
print(f"CAGR "+t+" :",cagr,"%")
print(f"CAGR over benchmark:",diff_benchmark,"%")
print(f"Treynor ratio:", treynor_ratio)
print("")
print(tabulate([["Return over the period:",df_return],["Return YTD:", df_ytd_return],["Return over 6 months:", df_6m_return], ["Return over 1 year:", df_1y_return], ["Return over 2 years:", df_2y_return]], headers=["Indicators", "in %"]))
print(tabulate([["Bench return over the period:",bench_return],["Bench return YTD", bench_ytd_return],["Bench return over 6 months:", bench_6m_return], ["Bench return over 1 year", bench_1y_return], ["Bench return over 2 years", bench_2y_return]], headers=["", ""]))
print("")
