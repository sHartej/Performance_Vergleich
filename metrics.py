import pandas as pd
import numpy as np

def sharpe_ratio(daily_returns):
   risk_free_daily = 0.04/252 # 
   rendite = daily_returns.mean()
   volatility = daily_returns.std()

   sharpe = ((rendite - risk_free_daily)/volatility) * 252**0.5

   return sharpe

def sortino_ratio(daily_returns_sortino):

   downside = daily_returns_sortino[daily_returns_sortino < 0]
   risk_free_daily = 0.04/252
   rendite = daily_returns_sortino.mean()
   volatility = downside.std()

   sortino = ((rendite - risk_free_daily)/volatility) * 252**0.5

   return sortino

def calculate_beta(data_funds, benchmark_funds):
   
   results = {}
   for funds in data_funds.columns:
      results[funds] = {}
      for benchmark in benchmark_funds.columns:
         kovarianz = np.cov(data_funds[funds], benchmark_funds[benchmark])[0,1]
         varianz = np.var(benchmark_funds[benchmark])

         results[funds][benchmark] = kovarianz/varianz

   return results

def calculate_alpha(data_funds_a, benchmark_funds_a):

   results = {}
   betas = calculate_beta(data_funds_a, benchmark_funds_a)

   for fund in data_funds_a.columns:
      results[fund] = {}
      for bench in benchmark_funds_a.columns:
         rendite = data_funds_a[fund].mean() * 252
         rendite_bench = benchmark_funds_a[bench].mean() * 252
         beta = betas[fund][bench]
         alpha = rendite - (0.04 + beta * (rendite_bench - 0.04))

         results[fund][bench] = alpha

   return results

def calculate_max_drawdown(data_fund_md):
   
   cumulative = (1 + data_fund_md).cumprod()
   rolling_max = cumulative.cummax()
   drawdown = ((cumulative - rolling_max) / rolling_max) * 100

   max_drawdown = drawdown.min()

   return max_drawdown

def calculate_recovery_period(data_fund_md):
    results = {}
    
    for fund in data_fund_md.columns:
        cumulative = (1 + data_fund_md[fund]).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = (cumulative - rolling_max) / rolling_max
        
        trough_date = drawdown.idxmin()
        recovery_date = cumulative[trough_date:][cumulative[trough_date:] >= rolling_max[trough_date]].first_valid_index()
        
        if recovery_date is None:
            results[fund] = "Not recovered"
        else:
            results[fund] = (recovery_date - trough_date).days
    
    return results