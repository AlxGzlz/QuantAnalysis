#################################################################################################
#Sortino and Sharpe ratios analysis, based on ./risk_ratio_analysis.py
def calculate_ratios(df):
    a = pd.DataFrame()
    #calculate the rolling Sharpe ratio
    #by default, the rolling period is 152 days
    a['rolling_sharpe'] = qt.stats.rolling_sharpe(df_returns, rolling_period=252)
    #calculate the rolling Sortino ratio
    #by default, the rolling period is 152 days
    a['rolling_sortino'] = qt.stats.rolling_sortino(df_returns, rolling_period=252)
    #identify when Sharpe ratio is below 0
    a['sharpe below 0'] = pta.below_value(a['rolling_sharpe'], 0)
    #identify when Sortino ratio is below 0
    a['sortino below 0'] = pta.below_value(a['rolling_sortino'], 0)
    return a

ratio_analysis = calculate_ratios(df_returns)

#count the total number of different values in the select dataset
def count_rows(df, column_name):
    value_counts = df[column_name].value_counts()
    count = value_counts.to_dict()
    business_days = count[0] + count[1]
    def av_negative(days, count):
        av_neg=(days-count[1])/days*100
        return av_neg
    def av_positive(days, count):
        av_pos=(days-count[0])/days*100
        return av_pos
    neg = av_negative(business_days, count)
    pos = av_positive(business_days,count)
    return neg, pos

av_ratios = count_rows(ratio_analysis,'sortino below 0'), count_rows(ratio_analysis,'sharpe below 0')

#identify between the Sharpe and the Sortino ratios in order to identify the risk-return of the asset along the time period
#negative result means that the Sortino ratio is higher than the Sharpe ratio, meaning that there is a high volatility correlated with high risk
#therefore the return of the asset is not guaranteed and can be low, or negative for the undergone exposure
def calculate_diff_av(a,b):
    c = a - b
    return c
    
diff_av = calculate_diff_av(ratio_analysis['rolling_sharpe'], ratio_analysis['rolling_sortino'])

#identify the skewed returns of the selected asset
#based on post https://www.quora.com/What-does-a-Sortino-number-that-is-higher-than-the-Sharpe-number-mean-statistically
def skewed_returns(sortino, sharpe): 
    if sortino > sharpe * 1.7:
        return "positive skewed returns"
    elif (sortino <= sharpe * 1.7) and (sortino > sharpe * 1.4):
        return "neutral skewed returns"
    elif sortino <= sharpe * 1.4:
        return "negative skewed returns"  

result = skewed_returns(sortino_ratio,sharpe_ratio)
#################################################################################################
#################################################################################################
#calculate the average price of the asset over the loaded time period
def av_price(df, column):
    av_price = float(np.mean(df[column]))
    av_price = round(av_price, 2)
    df['Average price'] = av_price
    return df

df_day = av_price(df_day,'Close')

#based on the PQN025 Newsletter (https://pyquantnews.com/kalman-filter-openbb-for-parameterless-indicators/)
#computation of the Kalman Ratio for the closing prices of the asset
#compute the Kalman ratio for the asset price
def compute_Kalman(df,column):
    kf = KalmanFilter(transition_matrices = [1],observation_matrices = [1],initial_state_mean = 0,initial_state_covariance = 1,observation_covariance=1,transition_covariance=0.01)
    state_means, _ = kf.filter(df[column])
    df['Kalman price'] = state_means
    return df

df_day = compute_Kalman(df_day,'Close')
#################################################################################################
#################################################################################################
#calculate the YTD return for a selected asset
def calculate_ytd_returns(df,column):
    jan_1st_year = datetime(datetime.now().year, 1, 1)
    ytd = df.loc[df.index >= jan_1st_year]
    returns=qt.stats.compsum(ytd)*100
    returns=returns.tail(1)
    returns=float(returns[column])
    return returns

#compute the average return of the asset over the defined time period  
def calculate_av_return(df,column,days):
    returns=qt.stats.compsum(df.tail(days))*100
    returns=returns.tail(1)
    returns=float(returns[column])
    return returns

calculate_av_return(df_returns,"Close",259)

#compute the YTD return of the asset & the benchmark
df_ytd_return=calculate_ytd_returns(df_returns,'Close')
bench_ytd_return=calculate_ytd_returns(bench_returns,'Close')

#compute the returns for the other defined time periods
#if the defined time period is shorter than one of the define period below, the result will be equal for both of them
#ex: for a selection of 300 days, df_2y_return = df_return, even if it is not the case
df_6m_return = calculate_av_return(df_returns,"Close",125)
df_1y_return = calculate_av_return(df_returns,"Close",259)
df_2y_return = calculate_av_return(df_returns,"Close",519)
df_period_return = calculate_av_return(df_returns,"Close",10000)
bench_6m_return = calculate_av_return(bench_returns,"Close",125)
bench_1y_return = calculate_av_return(bench_returns,"Close",259)
bench_2y_return = calculate_av_return(bench_returns,"Close",519)
bench_period_return = calculate_av_return(bench_returns,"Close",10000)

#################################################################################################
#################################################################################################
def return_comparison(a,b):
    c = (a*100)-b
    c = round(c,3)
    return c

#compare the asset cagr with the benchmark's return
diff_benchmark = return_comparison(cagr, bench_period_return)

#compute the compounded total return over the loaded period
def compound_return(df):
    cpd = qt.stats.compsum(df)
    return cpd

cpd_return = compound_return(df_returns)
bench_cpd_return = compound_return(bench_returns)

#compute the rolling volatility of returns over the period
def rolling_volatility(returns, period):
    rolling_volatility = qt.stats.rolling_volatility(returns, period)
    return rolling_volatility

df_rolling_vol = rolling_volatility(df_returns, days)
bench_rolling_vol = rolling_volatility(bench_returns, days)

#compute the RSI & RSX indicators
df_day['RSX']=pta.rsx(df_day['Close'].tail(90), length=14, drift=1, offset=0)
df_day['RSI']=pta.rsi(df_day['Close'].tail(90), length=14, drift=1, offset=0)
bench_day['RSI'] = pta.rsi(bench_day['Close'].tail(65), length=14, drift=1, offset=0)

#################################################################################################
#################################################################################################
#plot the results
%matplotlib widget
figure, axis = plt.subplots(3,1, figsize=(15,15))
#plot the price & Kalman price of the asset
axis[0].set_title("Daily evolution of price of "+t)
axis[0].set_ylabel("price in $")
axis[0].plot(df_day['Close'], label="price", c="blue")
axis[0].plot(df_day['Kalman price'], label='Kalman', c="orange")
axis[0].plot(df_day['Average price'], label="avg price over the period", c="red")
axis[0].legend(loc="upper right")
#plot the compounded returns of the asset and the benchmark
axis[1].set_title("Compounded returns over the period")
axis[1].set_ylabel("% return")
axis[1].plot(cpd_return,label=t,c="blue")
axis[1].plot(bench_cpd_return, label=b,c="orange")
axis[1].legend(loc='upper right')
#plot the Sharpe and Sortino ratios
axis[2].set_title("Sharpe & Sortino trend "+t)
axis[2].plot(ratio_analysis['rolling_sharpe'], label = "Sharpe ratio", c="green")
axis[2].plot(ratio_analysis['rolling_sortino'], label = "Sortino ratio", c="orange")
axis[2].plot(diff_av, label="Sortino>Sharpe", c="red")

figure, axis = plt.subplots(2,1, figsize=(15,15))
#plot the volatility of the asset
axis[0].set_title("Rolling volatility")
axis[0].set_ylabel("Volatility ratio")
axis[0].plot(df_rolling_vol,label=t)
axis[0].plot(bench_rolling_vol,label=b)
axis[0].legend(loc='upper right')
#plot the RSI & RSX of the asset
axis[1].set_title("RSI & RSX evolution")
axis[1].plot(df_day['RSX'],label ='RSX', color='r')
axis[1].plot(df_day['RSI'],label ='RSI', color='b')
axis[1].plot(bench_day['RSI'],label='bench RSI',color='g')
axis[1].legend(loc='upper right')
print("")
print("Over the period:")
print(f"CAGR "+t+" :",cagr,"%")
print(f"CAGR over benchmark:",diff_benchmark,"%")
print(f"Treynor ratio:",treynor_ratio)
print("")
print(tabulate([["Return over the period:",df_period_return],["Return YTD:", df_ytd_return],["Return over 6 months:", df_6m_return], ["Return over 1 year:", df_1y_return], ["Return over 2 years:", df_2y_return]], headers=["Indicators", "in %"]))
print(tabulate([["Bench return over the period:",bench_period_return],["Bench return YTD", bench_ytd_return],["Bench return over 6 months:", bench_6m_return], ["Bench return over 1 year", bench_1y_return], ["Bench return over 2 years", bench_2y_return]], headers=["", ""]))
print("")
print("---------------------------------------")
print(f"Latest computed Sharpe ratio:", sharpe_ratio)
print(f"Latest computed Sortino ratio:", sortino_ratio)
print("")
print(f"Skewed Returns: {result}")
print("")
print(tabulate([["Sortino ratio below 0:",av_ratios[0][0]],["Sortino ratio above 0:", av_ratios[0][1]]], headers=["Indicators", "in %"]))
print(tabulate([["Sharpe ratio below 0:", av_ratios[1][0]],["Sharpe ratio above 0:", av_ratios[1][1]]],headers=["", "     "]))
print("------------------------------")
