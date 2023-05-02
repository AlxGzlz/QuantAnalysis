import yfinance as yf
import quantstats as qt
import pyfolio as pf

import pandas as pd
import pandas_ta as pta
import numpy as np
import matplotlib.pyplot as plt
import ipympl as mpl
import statsmodels.api as sm
import math
import re

from arch import arch_model
from pykalman import KalmanFilter
from statsmodels import regression
from tabulate import tabulate
from datetime import datetime

class portfolioReturns:
    def __init__(self, ticker, portfolio, bench, risk_free, timeperiod="2y"):
        self.ticker = ticker
        self.portfolio = portfolio
        self.bench = bench
        self.risk_free = risk_free[0]
        self.timeperiod = timeperiod
        self.days = int(re.findall(r'\d+', timeperiod)[0])
        self.time = 24
        
        self.df_day = yf.download(self.ticker, period=self.timeperiod)
        self.pf_day = yf.download(self.portfolio, period=self.timeperiod)
        self.bench_day = yf.download(self.bench, period=self.timeperiod)
        self.riskfree_day = yf.download(self.risk_free, period=self.timeperiod)
        
        self.df_returns = pd.DataFrame(self.df_day['Close'].pct_change().dropna())
        self.bench_returns = pd.DataFrame(self.bench_day['Close'].pct_change().dropna())
        self.riskfree_returns = pd.DataFrame(self.riskfree_day['Close'].pct_change().dropna())
        self.pf_returns = pd.DataFrame(self.pf_day['Close'].pct_change().dropna())


class riskIndicators:    
    def __init__(self, df_day, bench_day, df_returns, bench_returns, riskfree_returns):
        self.df_day = df_day
        self.bench_day = bench_day
        self.df_returns = df_returns
        self.bench_returns = bench_returns
        self.riskfree_returns = riskfree_returns
        self.cagr = self.get_cagr()
        self.treynor_ratio = self.get_treynor_ratio()
        self.sharpe_ratio = self.get_sharpe_ratio()
        self.sortino_ratio = self.get_sortino_ratio()
        self.ratio_analysis = self.calculate_ratios()
        self.skewness = self.get_skewed_returns()
        self.rol_vol = self.rolling_volatility()
    
    # Compute the Compound Annual Growth Rate
    def get_cagr(self):
        cagr = qt.stats.cagr(self.df_day['Close'])
        cagr = float(cagr)
        cagr = round(cagr, 5)
        bench_cagr = qt.stats.cagr(self.bench_day['Close'])
        bench_cagr = float(bench_cagr)
        bench_cagr = round(bench_cagr, 5)
        return cagr, bench_cagr

    # Compute the Treynor ratio of the loaded instrument
    # The Treynor ratio estimates the excess return of the asset comparing to a risk-free asset
    # https://www.investopedia.com/terms/t/treynorratio.asp
    def get_treynor_ratio(self):
        treynor_ratio = qt.stats.treynor_ratio(self.df_returns, self.riskfree_returns)
        treynor_ratio = float(treynor_ratio)
        treynor_ratio = round(treynor_ratio, 5)
        return treynor_ratio

    # Compute Sharpe ratio of the loaded instrument
    def get_sharpe_ratio(self):
        # Get the Sharpe ratio based on the number of loaded days
        sharpe_ratio = float(pta.sharpe_ratio(self.df_day['Close'], 0))
        sharpe_ratio = round(sharpe_ratio, 4)
        return sharpe_ratio

    # Compute Sortino ratio of the loaded instrument
    # The Sortino ratio is the calculation of the expected return compared to a free-risk asset,
    # divided by the downside standard deviation
    # https://breakingdownfinance.com/finance-topics/performance-measurement/sortino-ratio/
    def get_sortino_ratio(self):
        sortino_ratio = qt.stats.sortino(self.df_returns, periods=252)
        sortino_ratio = float(sortino_ratio)
        sortino_ratio = round(sortino_ratio, 4)
        return sortino_ratio

    def calculate_ratios(self):
        ratios = pd.DataFrame()
        ratios['rolling_sharpe']=qt.stats.rolling_sharpe(asset_returns,rf=0, rolling_period=252)
        ratios['rolling_sortino']=qt.stats.rolling_sortino(asset_returns,rf=0, rolling_period=252)
        ratios['sharpe below 0'] = ratios['rolling_sharpe'].apply(lambda x: x < 0)
        ratios['sortino below 0'] = ratios['rolling_sortino'].apply(lambda x: x < 0)
        ratios['sortino above sharpe']=ratios['rolling_sortino']-ratios['rolling_sharpe']
        return ratios

    #based on the Sharpe and the Sortino ratios, this function helps  to identify the trend in the asset results observed
    #during the time period
    def get_skewed_returns(self):
        def skewed_returns(self, sortino, sharpe): 
            if sortino > sharpe * 1.7:
                return "positive skewed returns"
            elif (sortino <= sharpe * 1.7) and (sortino > sharpe * 1.4):
                return "neutral skewed returns"
            elif sortino <= sharpe * 1.4:
                return "negative skewed returns"  
        result = skewed_returns(self, self.sortino_ratio, self.sharpe_ratio)
        return result
    
    #compute the rolling volatility of returns over one year
    def rolling_volatility(self):
        rol_vol = qt.stats.rolling_volatility(self.df_returns,252)
        bench_rol_vol = qt.stats.rolling_volatility(self.bench_returns,252)
        return rol_vol, bench_rol_vol

###################################################   
    #calculate the average price and the price with the Kalman filter
class PriceTrend:
    def __init__(self, asset_price, benchmark_price):
        self.df_day = asset_price
        self.bench_day = benchmark_price
        self.average_price = self.get_average_price("Close")
        self.kalman_price = self.compute_Kalman("Close")
        self.rsi=self.R_S_Indicators()
    
    def get_average_price(self,column):
        av_price = float(np.mean(self.df_day[column]))
        av_price = round(av_price, 2)
        self.df_day['Average price'] = av_price
        return self.df_day['Average price']

    #the Kalman filter helps to reduce the noise in the definition of the trend of an asset price   
    def compute_Kalman(self, column):
        kf = KalmanFilter(transition_matrices=[1], observation_matrices=[1], initial_state_mean=0, initial_state_covariance=1, observation_covariance=1, transition_covariance=0.01)
        state_means, _ = kf.filter(self.df_day[column])
        self.df_day['Kalman price'] = state_means
        return self.df_day
    
    #compute the RSI & RSX indicators + RSI for the benchmark
    def R_S_Indicators(self):
        self.df_day['RSX']=pta.rsx(self.df_day['Close'].tail(90), length=14, drift=1, offset=0)
        self.df_day['RSI']=pta.rsi(self.df_day['Close'].tail(90), length=14, drift=1, offset=0)
        self.bench_day['RSI']=pta.rsi(self.bench_day['Close'].tail(65), length=14, drift=1, offset=0)

    ############################################################
    #calculate the performance of the selected asset and its benchmark over different time periods
class AssetPerformance:
    def __init__(self, my_portfolio, df_returns, bench_returns, days):
        self.df_day=my_portfolio.df_day['Close']
        self.bench_day=my_portfolio.bench_day['Close']
        self.df_returns = asset_returns
        self.bench_returns = bench_returns
        self.days = days
        self.asset_performance = self.compute_returns(self.df_returns,"Close")
        self.bench_performance = self.compute_bench_returns(self.bench_returns,"Close")
        
    def calculate_ytd_returns(self, df,column):
        jan_1st_year = datetime(datetime.now().year, 1, 1)
        ytd = df.loc[df.index >= jan_1st_year]
        returns = qt.stats.compsum(ytd) * 100
        returns = returns.tail(1)
        returns = returns[column]
        return returns
    
    def calculate_av_return(self, df,days):
        returns = qt.stats.compsum(df.tail(days)) * 100
        returns = returns.tail(1)
        returns = float(returns['Close'])
        return returns
    
    def compute_period_returns(self, df):
        period_return =self.calculate_av_return(df,self.days)
        _3month_return=self.calculate_av_return(df,94)
        _6month_return=self.calculate_av_return(df,126)
        _1year_return=self.calculate_av_return(df,252)
        _2year_return=self.calculate_av_return(df,504)
        return period_return,_3month_return, _6month_return, _1year_return, _2year_return
    
    def compute_returns(self,df_r,column):
        ytd_return = self.calculate_ytd_returns(df_r,column)
        returns = self.compute_period_returns(df_r)
        return ytd_return, returns
    
    def compute_bench_returns(self,df_r,column):
        bench_ytd_return = self.calculate_ytd_returns(df_r,column)
        bench_returns = self.compute_period_returns(df_r)
        return bench_ytd_return, bench_returns     
    #########################################################################
    #print the dashboard with all the calculated indicators
class PrintDashboard:
    def __init__(self,risk_indicators, asset_trend, asset_price, asset_perf,ticker,benchmark):
        self.ticker=ticker
        self.benchmark=benchmark
        self.sharpe_ratio=risk_indicators.sharpe_ratio
        self.sortino_ratio=risk_indicators.sortino_ratio
        self.treynor_ratio=risk_indicators.treynor_ratio
        self.skewness=risk_indicators.skewness
        self.rol_vol=risk_indicators.rol_vol
        self.cagr=risk_indicators.cagr
        self.ratio_analysis=risk_indicators.ratio_analysis
        self.asset_price=asset_price
        self.average_price=asset_trend.average_price
        self.kalman=asset_trend.kalman_price['Kalman price']
        self.bench_performance=asset_perf.bench_performance
        self.asset_performance=asset_perf.asset_performance
        self.asset_returns=risk_indicators.df_returns
        self.bench_returns=risk_indicators.bench_returns
        self.bench_price=risk_indicators.bench_day
        self.dashboard=self.display_plots()
    
    def display_plots(self): 
        %matplotlib widget
        # plot the results
        figure, axis = plt.subplots(5,1, figsize=(15,20))
        # plot the price & Kalman price of the asset
        axis[0].set_title("Daily evolution of price of "+self.ticker)
        axis[0].set_ylabel("price in $")
        axis[0].plot(self.asset_price['Close'], label="price", c="blue")
        axis[0].plot(self.kalman, label='Kalman', c="orange")
        axis[0].plot(self.average_price, label="avg price over the period", c="red")
        axis[0].legend(loc="upper left")
        # plot the compounded returns of the asset and the benchmark
        axis[1].set_title("Daily returns over the period")
        axis[1].set_ylabel("% return")
        axis[1].plot(self.asset_returns,label=self.ticker,c="blue")
        axis[1].plot(self.bench_returns, label=self.benchmark,c="orange")
        axis[1].legend(loc='upper left')
        #plot the Sharpe and Sortino ratios
        axis[2].set_title("Sharpe & Sortino trend "+ticker)
        axis[2].plot(self.ratio_analysis['rolling_sharpe'], label = "Sharpe ratio", c="green")
        axis[2].plot(self.ratio_analysis['rolling_sortino'], label = "Sortino ratio", c="orange")
        axis[2].plot(self.ratio_analysis['sortino above sharpe'], label="", c="red")
        axis[2].legend(loc='upper left')
        #plot the rolling volatility of both the asset and the benchmark
        axis[3].set_title("Rolling volatility")
        axis[3].set_ylabel("Volatility ratio")
        axis[3].plot(self.rol_vol[0],label=self.ticker)
        axis[3].plot(self.rol_vol[1],label=self.benchmark)
        axis[3].legend(loc='upper left')
        #plot the RSI & RSX of the asset + RSI of the benchmark
        axis[4].set_title("RSI & RSX evolution")
        axis[4].plot(self.asset_price['RSX'],label ='RSX', color='r')
        axis[4].plot(self.asset_price['RSI'],label ='RSI', color='b')
        axis[4].plot(self.bench_price['RSI'],label='bench RSI',color='g')
        axis[4].legend(loc='upper left')
        #plot the indicators
        print("")
        print("Over the period:")
        print(f"CAGR "+self.ticker+" :",self.cagr[0],"%")
        print(f"Benchmark CAGR",self.cagr[1],"%")
        print(f"Treynor ratio:",self.treynor_ratio)
        print("")
        print(tabulate([["Return over the period:",self.asset_performance[1][0]],["Return YTD:", self.asset_performance[0][0]],["Return over 6 months:", self.asset_performance[1][1]], ["Return over 1 year:", self.asset_performance[1][2]], ["Return over 2 years:", self.asset_performance[1][3]]], headers=["Indicators", "in %"]))
        print(tabulate([["Bench return over the period:",self.bench_performance[1][0]],["Bench return YTD", self.bench_performance[0][0]],["Bench return over 6 months:", self.bench_performance[1][1]], ["Bench return over 1 year", self.bench_performance[1][2]], ["Bench return over 2 years", self.bench_performance[1][3]]], headers=["", ""]))
        print("")
        print("---------------------------------------")
        print(f"Latest computed Sharpe ratio:", self.sharpe_ratio)
        print(f"Latest computed Sortino ratio:", self.sortino_ratio)
        print("")
        print(f"Skewed Returns: {self.skewness}")
        print("")
        print("------------------------------")

ticker = "YOUR_TICKER"
portfolio = "YOUR_PORTFOLIO"
bench = ["YOUR BENCHMARK"]
risk_free = ["YOUR RISK-FREE ASSET"]
#preferred timeperiod option: "2y"
timperiod="YOUR TIMEPERIOD"

my_portfolio = portfolioReturns(ticker, portfolio, bench, risk_free)       

#define the conditions for the computation
asset_price = my_portfolio.df_day
benchmark_price = my_portfolio.bench_day
asset_returns = my_portfolio.df_returns
benchmark_returns = my_portfolio.bench_returns
riskfree_returns = my_portfolio.riskfree_returns
days = 504

#calculate the risk indicators
risk_indicators = riskIndicators(asset_price, benchmark_price, asset_returns, benchmark_returns, riskfree_returns)
#calculate the price trend of the selected asset
asset_trend = PriceTrend(asset_price, benchmark_price)
#calculate the performance indicators
asset_perf = AssetPerformance(my_portfolio,asset_returns, benchmark_returns, days)
#display the calculated indicators in a dashboard
dashboard = PrintDashboard(risk_indicators, asset_trend, asset_price, asset_perf,ticker,bench)
