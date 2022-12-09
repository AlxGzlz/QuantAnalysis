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

#plot the drawdown registered on the selected tim period
plt.title("Drawdown chart")
plt.xlabel('datetime')
plt.ylabel("% drawdown")
plt.plot(df_drawdown['DD_PCT'], label='drawdown',c='r')
plt.legend
plt.show
print(f"High Range (in %): {high_range}")
print(f"Low Range (in %): {low_range}")
