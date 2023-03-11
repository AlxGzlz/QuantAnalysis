#based on PQN020 Newsletter: "Seeking alpha? Hedge your beta with Python"
#https://pyquantnews.com/seeking-alpha-hedge-your-beta-with-python/
#hedge the beta of your selected ticker or portfolio
X = bench_returns.values
Y = df_returns.values
Z = riskfree_returns.values
#define the linear regression for the selected ticker
def linreg(x,y,z): 
    #add a column of ls to fit alpha
    x = sm.add_constant(x)
    model = regression.linear_model.OLS(y,x).fit()
    #remove the constant
    x = x[:, 1]
    return model.params[0], model.params[1]

alpha, beta = linreg(X,Y,Z)

#seek to hedge the beta of the selected ticker, meaning to get beta = 0
#be short a number of shares in the market equal to the beta plus ticker
hedged_portfolio = -1 * beta * bench_returns + df_returns
hedged_portfolio.name = "Heged Portfolio"
P = hedged_portfolio.values 
alpha, hedged_beta = linreg(X,P,Z)

#calculate the correlation in the price evolution between the selected asset and benchmark
def corrcoef(df,bc):
    a=np.corrcoef(df,bc)[0,1]
    a=round(a,4)
    return a

correlation_coef=corrcoef(df_day['Close'],bench_day['Close'])

print(f"Alpha:",alpha)
print(f"Beta:",beta)
print(f"Hedged Beta:",hedged_beta)
print(f"Correlation coefficient between "+t+" and "+b+" :",correlation_coef)

%matplotlib widget
plt.title("Prices correlation between"+t+" and "+b)
plt.ylabel(b)
plt.xlabel(t)
plt.scatter(df_day['Close'],bench_day['Close'])
