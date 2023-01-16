#define a dedicated DataFrame for the YTD data
def calculate_ytd_returns(a):
    jan_1st_year = datetime(datetime.now().year, 1, 1)
    ytd = a.loc[a.index >= jan_1st_year]
    return ytd

#compute the average return of the asset over the defined time period  
def calculate_av_return(a):
    b=qt.stats.compsum(a)*100
    c=b.tail(1)
    c=float(c['Close'])
    return c

#compute the YTD return of the asset & the benchmark
df_ytd = calculate_ytd_returns(df_returns)
df_ytd_return=calculate_av_return(df_ytd)
bench_ytd = calculate_ytd_returns(bench_returns)
bench_ytd_return=calculate_av_return(bench_ytd)

#compute the returns for the other defined time periods
#if the defined time period is shorter than one of the define period below, the result will be equal for both of them
#ex: for a selection of 300 days, df_2y_return = df_return, even if it is not the case
df_6m_return = calculate_av_return(df_returns.tail(129))
df_1y_return = calculate_av_return(df_returns.tail(259))
df_2y_return = calculate_av_return(df_returns.tail(519))
df_return = calculate_av_return(df_returns)
bench_6m_return = calculate_av_return(bench_returns.tail(129))
bench_1y_return = calculate_av_return(bench_returns.tail(259))
bench_2y_return = calculate_av_return(bench_returns.tail(519))
bench_return = calculate_av_return(bench_returns)

#adjust the format of the asset cagr data
cagr = float(risk_analysis['cagr'])
cagr =  round(cagr,5)

def return_comparison(a,b):
    c = (a*100)-b
    c = round(c,3)
    return c

#compare the cagr and the average return of the asset
diff_return  = return_comparison(cagr, df_return)
#compare the asset cagr with the benchmark's return  
diff_benchmark = return_comparison(cagr, bench_return)

%matplotlib widget
#plot the returns of the ticker and the benchmark on the selected time period
plt.title("")
plt.plot(df_returns, label=t, c="blue")
plt.plot(bench_returns,label=b, c="orange")
plt.xlabel("datetime")
plt.ylabel("daily return")
plt.legend()
plt.show()
print("")
print(f"CAGR "+t+" :",cagr,"%")
print(f"CAGR over benchmark:",diff_benchmark,"%")
print("")
print(tabulate([["Return over the period:",df_return],["Return YTD:", df_ytd_return],["Return over 6 months:", df_6m_return], ["Return over 1 year:", df_1y_return], ["Return over 2 years:", df_2y_return]], headers=["Indicators", "in %"]))
print(tabulate([["Bench return over the period:",bench_return],["Bench return YTD", bench_ytd_return],["Bench return over 6 months:", bench_6m_return], ["Bench return over 1 year", bench_1y_return], ["Bench return over 2 years", bench_2y_return]], headers=["", ""]))
