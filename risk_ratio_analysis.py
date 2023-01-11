ratio_analysis = pd.DataFrame()
#calculate the rolling Sharpe ratio over the loaded time period
ratio_analysis['rolling_sharpe'] = qt.stats.rolling_sharpe(df_returns, rolling_period=126)
#calculate the Sortino ratio over the loaded time period 
ratio_analysis['rolling_sortino'] = qt.stats.rolling_sortino(df_returns)

#compare when Sharpe ratio is above Sortino ratio
#when Sharpe ratio is below Sortino ratio:
#the risk to get/keep the asset is considerdd too high to get a higher return than a risk-free asset
ratio_analysis['sharpe above sortino'] = pta.above(ratio_analysis['rolling_sharpe'], ratio_analysis['rolling_sortino'])

#identify when Sharpe ratio is below 0
ratio_analysis['sharpe below 0'] = pta.below_value(ratio_analysis['rolling_sharpe'], 0)
#identify when Sortino ratio is below 0
ratio_analysis['sortino below 0'] = pta.below_value(ratio_analysis['rolling_sortino'], 0)

#count the total number of different values in the select dataset
def count_rows(df, column_name):
    value_counts = df[column_name].value_counts()
    return value_counts.to_dict()

#apply the above function for the historical results of the Sortino ratio above 0
sortino_rows = count_rows(ratio_analysis, 'sortino below 0')
#apply the above function for the historical results of the Sharpe ratio above 0
sharpe_rows = count_rows(ratio_analysis, 'sharpe below 0')
#apply the above function for the historical results of the Sharpe ratio above the Sortino ratio
risk_profit_rows = count_rows(ratio_analysis, 'sharpe above sortino')

#identify the % of days when the Sharpe ratio is under or above 0 during the selected time period
av_negative_sortino = ((days - sortino_rows[1]) - 1)/days*100
av_positive_sortino = ((days - sortino_rows[0]) - 1)/days*100
#identify the % of days when the Sharpe ratio is under or above 0 during the selected time period
av_negative_sharpe = ((days - sharpe_rows[1]) - 1)/days*100
av_positive_sharpe = ((days - sharpe_rows[0]) - 1)/days*100
#identify the % of days when the Sharpe ratio is under or above the Sortino ratio during the selected time period
av_negative_risk = ((days - risk_profit_rows[1]) - 1)/days*100
av_positive_risk = ((days - risk_profit_rows[0]) - 1)/days*100

if av_negative_sortino < av_positive_sortino:
    comment_av_sortino = 1
else: comment_av_sortino = 0,5
    
if av_negative_sharpe < av_positive_sharpe:
    comment_av_sharpe = 1
else: comment_av_sharpe = 0,5
    
if av_negative_risk < av_positive_risk:
    comment_av_risk = 2
else: comment_av_risk = 1
    
result_av = (float(comment_av_sortino) + float(comment_av_sharpe) + float(comment_av_risk)

if result_av >=3.5:
    return "risk mitigated over the period"
elif result_av == 3:
    return "significant risk over the period"
elif result_av >= 2:
    return "high risk/low return over the period"
