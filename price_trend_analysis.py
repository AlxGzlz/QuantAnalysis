#calculate the average price of the loaded time period
average_price = float(np.mean(df_day['Close']))
average_price = round(average_price, 2)
#integrate the average price in the dataframe of the loaded instrument
df_day['average price'] = average_price
#calculate the Simple Moving Average (sma)
sma = pta.sma(df_day["Close"])
#calculate the Exponential Moving Average
ema = pta.ema(df_day["Close"])

#based on the PQN025 Newsletter (https://pyquantnews.com/kalman-filter-openbb-for-parameterless-indicators/)
#computation of the Kalman Ratio for the closing prices of the asset
#define the parameter to compute the Kalman ratio
kf = KalmanFilter(
    transition_matrices = [1],
    observation_matrices = [1],
    initial_state_mean = 0,
    initial_state_covariance = 1,
    observation_covariance=1,
    transition_covariance=0.01)

#compute the Kalman ratio for the asset price*
def compute_Kalman(a):
    state_means, _ = kf.filter(a)
    state_means = pd.Series(state_means.flatten(), index=a.index)
    return state_means

Kalman_df = compute_Kalman(df_day['Close'])

%matplotlib widget
plt.title("Daily prices evolution of "+ ticker[0])
plt.plot(df_day['Close'], label="price", c="blue")
#plt.plot(sma, label ="SMA", c="green")
#plt.plot(ema, label = "EMA", c="yellow")
plt.plot(Kalman_df, label='Kalman', c="orange")
plt.plot(df_day['average price'], label="avg price over the period", c="red")
plt.xlabel("datetime")
plt.ylabel("price in $")
plt.legend()
plt.show()
