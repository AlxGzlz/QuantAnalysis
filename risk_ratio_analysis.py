ratio_analysis = pd.DataFrame()
#calculate the rolling Sharpe ratio over the loaded time period
ratio_analysis['rolling_sharpe'] = qt.stats.rolling_sharpe(df_returns)
#calculate the Sortino ratio over the loaded time period 
ratio_analysis['rolling_sortino'] = qt.stats.rolling_sortino(df_returns)

#compare when Sharpe ratio is above Sortino ratio
#when Sharpe ratio is below Sortino ratio:
#the risk to get/keep the asset is considerdd too high to get a higher return than a risk-free asset
ratio_analysis['sharpe above sortino'] = pta.above(ratio_analysis['rolling_sharpe'], ratio_analysis['rolling_sortino'])

#compare when Sharpe ratio is below 0
ratio_analysis['sharpe below 0'] = pta.below_value(ratio_analysis['rolling_sharpe'], 0)
#compare when Sortino ratio is below 0
ratio_analysis['sortino below 0'] = pta.below_value(ratio_analysis['rolling_sortino'], 0)

x = 0
y = x+1
#identify when the Sortino ratio goes above 0 => bullish signal
while ratio_analysis['sortino below 0'][x]==ratio_analysis['sortino below 0'][y]:
    x+=1
    if ratio_analysis['sortino below 0'][x]>ratio_analysis['sortino below 0'][y]:
    sortino_bullish_signal[x] = ratio_analysis.index[x]

#identify when the Sortino ratio goes below 0 => bearish signal
while ratio_analysis['sortino below 0'][x]==ratio_analysis['sortino below 0'][y]:
	x+=1
	if ratio_analysis['sortino below 0'][x]<ratio_analysis['sortino below 0'][y]:
	sortino_bearish_signal[x] = ratio_analysis.index[x]
	
#identify when the Sharpe ration goes above 0 => bullish signal
while ratio_analysis['sharpe below 0'][x]==ratio_analysis['sharpe below 0'][y]:
    x+=1
    if ratio_analysis['sharpe below 0'][x]>ratio_analysis['sharpe below 0'][y]:
    sharpe_bullish_signal[x] = ratio_analysis.index[x]

#identify when the Sharpe ration goes below 0 => bearish signal
while ratio_analysis['sharpe below 0'][x]==ratio_analysis['sharpe below 0'][y]:
    x+=1
    if ratio_analysis['sharpe below 0'][x]<ratio_analysis['sharpe below 0'][y]:
    sharpe_bearish_signal[x] = ratio_analysis.index[x]]
