#create DataFrame for the risk indicators
risk_analysis = pd.DataFrame(index=ticker)

#calculate the daily return for the loaded instrument and the loaded benchmark
df_returns = pd.DataFrame(df_day['close'].pct_change().dropna())
bench_returns = pd.DataFrame(bench_day['close'].pct_change().dropna())

#calculate the average return of the ticker
average_return = np.mean(df_returns, axis=0)

#calculate the standard deviation of the ticker
#https://www.investopedia.com/terms/s/standarddeviation.asp
std = float(np.std(df_returns))

#compute the Value-At-Risk of the loaded ticker
#with a level of confidence: 95%
#with a sigma (1-day return) of 1
#https://merage.uci.edu/~jorion/oc/case3.html
def get_var(df, sigma, confidence):
    var = qt.stats.var(df, sigma, confidence)
    return var

risk_analysis['var'] = get_var(df_returns, 1, 0.95)

#compute Sharpe ratio of the loaded instrument
def get_sharpe_ratio(df):
    #get the sharpe ratio based on number of loaded days
    sharpe_ratio = float(pta.sharpe_ratio(df['close'], 0))
    return sharpe_ratio

risk_analysis['sharpe ratio'] = get_sharpe_ratio(df_day)

#compute the Risk-return ratio of the loaded instrument
def get_risk_return_ratio(df):
    risk_return = float(qt.stats.risk_return_ratio(df))
    return risk_return
    
risk_analysis['risk-reward ratio'] = get_risk_return_ratio(df_returns)

#compute Sortino ratio of the loaded instrument
#the Sortino ratio is the calculation of the expected return compared to a free-risk asset,
#dividend by the downside standard deviation
#https://breakingdownfinance.com/finance-topics/performance-measurement/sortino-ratio/
def get_sortino_ratio(series, N, rf):
    mean = series.mean() * N -rf
    std_neg = series[series<0].std()*np.sqrt(N)
    return float(mean/std_neg)

risk_analysis['sortino ratio'] = get_sortino_ratio(df_returns, 252, 0.01)

#compute the Calmar ratio of the loaded instrument
#the Calmar ratio is used to  measure the estiated annual rate (Rp - Rf) divided by the maximal drawdown
#higher is the Calmar ratio, higher is the return on the defined time period
#https://corporatefinanceinstitute.com/resources/wealth-management/calmar-ratio/
def get_calmar_ratio(df):
    calmar_ratio = pta.calmar_ratio(df, method='percent')
    return calmar_ratio

risk_analysis['calmar ratio'] = get_calmar_ratio(df_day['close'])

#compute the volatility over the selected period of the loaded instrument
def get_volatility(df):
    volatility = float(qt.stats.volatility(df))
    return volatility

risk_analysis['volatility'] = get_volatility(df_returns)

#compute the Treynor ratio of the loaded instrument
def get_treynor_ratio(df, bench):
    treynor_ratio = qt.stats.treynor_ratio(df, bench)
    return treynor_ratio

risk_analysis['treynor ratio'] = get_treynor_ratio(df_returns, bench_returns)

#compute the maximum drawdown of the loaded instrument
def get_max_drawdown(df):
    max_drawdown = pta.max_drawdown(df_day['close'], all=True)
    return max_drawdown['percent']

risk_analysis['max drawdown'] = get_max_drawdown(df_day['close'])

#compute the Ulcer Index of the loaded instrument
def get_ulcer_index(df):
    ulcer_index = float(qt.stats.ulcer_index(df))
    return ulcer_index

risk_analysis['ulcer index'] = get_ulcer_index(df_returns)

#compute the Compound Annual Growth Rate
def get_cagr(df):
    cagr = pta.cagr(df)
    return cagr

risk_analysis['cagr'] = get_cagr(df_day['close'])
