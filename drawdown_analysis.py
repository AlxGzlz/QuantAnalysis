#calculate the drawdown
df_drawdown = pta.drawdown(df_day['close'], offset=0)

#calculate the average drawdown
average_drawdown = np.mean(df_drawdown['DD_PCT'], axis=0)

#calculate the maximum drawdown
max_drawdown = df_drawdown['DD_PCT'].max()

#calculate the standard deviation of the drawdown
std_drawdown = np.std(df_drawdown['DD_PCT'])

#compute the main range of drawdown values along the period
high_range = average_drawdown + std_drawdown
low_range = average_drawdown - std_drawdown

#compute the ratio between the high range of drawdown and the maximum drawdown
#if >=0,60, very high variations 
#if <0,60 and >=50, high variations
#if <50 and >=25, moderate variations
#if <25, low variations
variation_ratio = high_range/max_drawdown

#compute the ratio between the Calmar ratio and the CAGR ratio
#higher is the ratio, higher are the risk and the volatility to get a return
calmar_over_cagr = risk_analysis["calmar ratio"]/risk_analysis['cagr']

#plot the drawdown registered on the selected tim period
print(tabulate([["Average Drawdown:",average_drawdown*100],["High range:", high_range*100], ["Low range:", low_range*100],["Variation ratio:", variation_ratio*100]], headers=["Indicator", "in % (by default)"]))
print(f"if Low Range negative: it is positive 'drawdown'")
print("")
print(f"Calmar ratio:", round(float(risk_analysis['calmar ratio']), 4))
print(f"Coumpound Annual Growth Rate:", round(float(risk_analysis['cagr']), 4))
print(f"Calmar/CAGR:", round(float(calmar_over_cagr), 4))
%matplotlib widget
plt.title("Drawdown chart")
plt.xlabel('datetime')
plt.ylabel("% drawdown")
plt.plot(df_drawdown['DD_PCT']*100, label='drawdown',c='r')
plt.legend
plt.show()
