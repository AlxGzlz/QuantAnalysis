#based on PQN020 Newsletter: "Seeking alpha? Hedge your beta with Python"
#https://pyquantnews.com/seeking-alpha-hedge-your-beta-with-python/
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

#seek to hedge the beta of the selected ticker, meaning to get beta = 0
#be short a number of shares in the market equal to the beta plus ticker
hedged_portfolio = -1 * beta * bench_returns + df_returns
hedged_portfolio.name = "Heged Portfolio"
P = hedged_portfolio.values 
alpha, hedged_beta = linreg(X, P)

def linreg_pred(df,ind):
    pred = df*ind
    return pred

beta_pred=linreg_pred(df_day['Close'],beta)
hedgedbeta_pred=linreg_pred(df_day['Close'],hedged_beta)

#plot the results
%matplotlib widget
plt.title('Comparison between '+t+' price and its linear regression prediction')
plt.plot(df_day['Close'])
plt.plot(beta_pred)
plt.ylabel('Price in $')
plt.legend(['Asset','Linear Regression Prediction'])
print(f"Alpha:",alpha)
print(f"Beta:",beta)
print(f"Hedged Beta:",hedged_beta)
