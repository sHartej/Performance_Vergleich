from data import load_data, daily_returns_tickers, daily_returns_benchmark
from metrics import sharpe_ratio, sortino_ratio, calculate_alpha, calculate_max_drawdown, calculate_recovery_period
from scraper import get_all_ter

data, bench_data = load_data()


returns_data = daily_returns_tickers(data)
returns_benchmark = daily_returns_benchmark(bench_data)


sharpe = sharpe_ratio(returns_data)
sortino = sortino_ratio(returns_data)
alpha = calculate_alpha(returns_data, returns_benchmark)
max_drawdown = calculate_max_drawdown(returns_data)
recovery = calculate_recovery_period(returns_data)


ter = get_all_ter()


print("Sharpe Ratio:", sharpe)
print("Sortino Ratio:", sortino)
print("Alpha:", alpha)
print("Max Drawdown:", max_drawdown)
print("Recovery Period:", recovery)
print("TER:", ter)