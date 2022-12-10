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
#if >=0,75, very high variations 
#if <0,75 and >=50, high variations
#if <50 and >=25, moderate variations
#if <25, low variations
variation_ratio = high_range/max_drawdown

#plot the drawdown registered on the selected tim period
plt.title("Drawdown chart")
plt.xlabel('datetime')
plt.ylabel("% drawdown")
plt.plot(df_drawdown['DD_PCT']*100, label='drawdown',c='r')
plt.legend
plt.show
print(tabulate([["Average Drawdown:",average_drawdown*100],["High range:", high_range*100], ["Low range:", low_range*100],["Variation ratio:", variation_ratio*100]], headers=["Indicator", "in %"]))
print(f"if Low Range negative: it is positive 'drawdown'")
