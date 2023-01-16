ratio_analysis = pd.DataFrame()
#calculate the rolling Sharpe ratio over the loaded time period
#by default, the rolling period is 152 days
ratio_analysis['rolling_sharpe'] = qt.stats.rolling_sharpe(df_returns)
#calculate the Sortino ratio over the loaded time period 
#by default, the rolling period is 152 days
ratio_analysis['rolling_sortino'] = qt.stats.rolling_sortino(df_returns)

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

#determine the number of business days indexed in the DataFrame
business_days = sortino_rows[0] + sortino_rows[1]
#identify the % of days when the Sharpe ratio is under or above 0 during the selected time period
av_negative_sortino = ((business_days - sortino_rows[1]))/business_days*100
av_positive_sortino = ((business_days - sortino_rows[0]))/business_days*100
#identify the % of days when the Sharpe ratio is under or above 0 during the selected time period
av_negative_sharpe = ((business_days - sharpe_rows[1]))/business_days*100
av_positive_sharpe = ((business_days - sharpe_rows[0]))/business_days*100

#identify between the Sharpe and the Sortino ratios in order to identify the risk-return of the asset along the time period
#negative result means that the Sortino ratio is higher than the Sharpe ratio, meaning that there is a high volatility correlated with high risk
#therefore the return of the asset is not guaranteed and can be low, or negative for the undergone exposure
def calculate_diff_av(a,b):
    c = a - b
    return c
    
diff_av_period = calculate_diff_av(ratio_analysis['rolling_sharpe'], ratio_analysis['rolling_sortino'])

#identify the skewed returns of the selected asset
#based on post https://www.quora.com/What-does-a-Sortino-number-that-is-higher-than-the-Sharpe-number-mean-statistically
def skewed_returns(sortino, sharpe): 
    if sortino > sharpe * 1.7:
        return "positive skewed returns"
    elif (sortino <= sharpe * 1.7) and (sortino > sharpe * 1.4):
        return "neutral skewed returns"
    elif sortino <= sharpe * 1.4:
        return "negative skewed returns"  

result = skewed_returns(int(risk_analysis['sortino ratio']), int(risk_analysis['sharpe ratio']))

#plot the graph comparing the Sharpe and the Sortino ratios + the analysis over the three mentioned ratios
%matplotlib widget
plt.title("Sharpe and Sortino ratios of "+ticker[0])
plt.plot(ratio_analysis['rolling_sharpe'], label = "Sharpe ratio", c="green")
plt.plot(ratio_analysis['rolling_sortino'], label = "Sortino ratio", c="orange")
plt.plot(diff_av_period, label="Sortino>Sharpe", c="red")
plt.xlabel("date")
plt.legend()
plt.show()
print(f"Latest computed Sharpe ratio:", round(float(risk_analysis['sharpe ratio']),4))
print(f"Latest computed Sortino ratio:", round(float(risk_analysis['sortino ratio']),4))
print("")
print(f"Skewed Returns: {result}")
print("")
print(tabulate([["Sortino ratio below 0:",av_negative_sortino],["Sortino ratio above 0:", av_positive_sortino]], headers=["Indicators", "in %"]))
print(tabulate([["Sharpe ratio below 0:", av_negative_sharpe],["Sharpe ratio above 0:", av_positive_sharpe]],headers=["", "     "]))
print("-----------------------------------")
