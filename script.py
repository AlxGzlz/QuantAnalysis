import twelvedata as td
import yfinance as yf
import quantstats as qt

import pandas as pd
import pandas_ta as pta
import mplfinance as mpl
import numpy as np
import matplotlib.pyplot as plt

from arch import arch_model
from twelvedata import TDClient

#define ticker(s) to analyze
ticker = ["ETH/USD"]
bench = ["GSPC"]
days = 90
time = 24

# Initialize client - apikey parameter is requiered
td=TDClient(apikey="SECRET_API_KEY")

#retrieve all prices data for a specific ticker on a defined time period
price_day = td.time_series(
    symbol=ticker,
    interval="1day",
    outputsize=days,
    timezone="UTC")

df_day = price_day.as_pandas()

#retrieve all prices data for benchmark ticker on the same time period
bench_price_day = td.time_series(
    symbol=bench,
    interval="1day",
    outputsize=days,
    timezone="UTC")

bench_day = bench_price_day.as_pandas()

#create DataFrame for the risk indicators
risk_analysis = pd.DataFrame(index=ticker)

#calculate the daily return for the loaded instrument and the loaded benchmark
df_returns = df_day['close'].pct_change().dropna()
bench_returns = bench_day['close'].pct_change().dropna()

#compute the Value-At-Risk of the loaded instrument
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
    risk_return = qt.stats.risk_return_ratio(df)
    
risk_analysis['risk-return ratio'] = get_risk_return_ratio(df_returns)

#compute Sortino ratio of the loaded instrument
def get_sortino_ratio(series, N,rf):
    mean = series.mean() * N -rf
    std_neg = float(series[series<0].std()*np.sqrt(N))
    return mean/std_neg

risk_analysis['sortino ratio'] = get_sortino_ratio(df_returns, 252, 0.01)

#compute the Calmar ratio of the loaded instrument
def get_calmar_ratio(df):
    calmar_ratio = pta.calmar_ratio(df, method='percent', years=1)
    return calmar_ratio

risk_analysis['calmar ratio'] = get_calmar_ratio(df_day['close'])

#compute the volatility over the selected period of the loaded instrument
def get_volatility(df):
    volatility = qt.stats.volatility(df)
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
    ulcer_index = qt.stats.ulcer_index(df)
    return ulcer_index

risk_analysis['ulcer index'] = get_ulcer_index(df_returns)

#compute the Compound Annual Growth Rate of the loaded instrument
def get_cagr(df):
    cagr = pta.cagr(df)
    return cagr

risk_analysis['cagr'] = get_cagr(df_day['close'])

print(risk_analysis)
