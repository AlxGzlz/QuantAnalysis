#hedge the beta of your selected ticker or portfolio
X = bench_returns.values
Y = df_returns.values

#define the linear regression for the selected ticker
def linreg(x,y): 
    #add a column of ls to fit alpha
    x = sm.add_constant(x)
    model = regression.linear_model.OLS(y,x).fit()
    #remove the constant
    x = x[:, 1]
    return model.params[0], model.params[1]

alpha, beta = linreg(X,Y)
print(f"Alpha: {alpha}")
print(f"Beta: {beta}")

X2 = np.linspace(X.min(), X.max(), 100)
Y_hat = X2 * beta - alpha

#plot the raw data
plt.scatter(X, Y, alpha=0.3)
plt.xlabel("Bench Daily Return")
plt.ylabel("Ticker Daily Return")
#add the regression line
plt.plot(X2, Y_hat, 'r', alpha=0.9)

#seek to hedge the beta of the selected ticker, meaning to get beta = 0
#be short a number of shares in the market equal to the beta plus ticker
hedged_portfolio = -1 * beta * bench_returns + df_returns
hedged_portfolio.name = "Heged Portfolio"

P = hedged_portfolio.values 
alpha, beta = linreg(X, P)
print(f"Hedged_Beta: {beta}")
