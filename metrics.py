import pandas as pd
import numpy as np

from config import RISK_FREE, TRADING_DAYS


def sharpe_ratio(daily_returns, risk_free=RISK_FREE):
    risk_free_daily = risk_free / TRADING_DAYS
    rendite = daily_returns.mean()
    volatility = daily_returns.std()

    sharpe = ((rendite - risk_free_daily) / volatility) * TRADING_DAYS ** 0.5

    return sharpe


def sortino_ratio(daily_returns_sortino, risk_free=RISK_FREE):
    risk_free_daily = risk_free / TRADING_DAYS
    rendite = daily_returns_sortino.mean()
    # Abwaerts-Volatilitaet: nur negative Renditen
    downside = daily_returns_sortino[daily_returns_sortino < 0]
    volatility = downside.std()

    sortino = ((rendite - risk_free_daily) / volatility) * TRADING_DAYS ** 0.5

    return sortino


def calculate_beta(data_funds, benchmark_funds):
    results = {}
    for fund in data_funds.columns:
        results[fund] = {}
        for benchmark in benchmark_funds.columns:
            # Gemeinsame Tage verwenden, damit cov/var konsistent sind
            paired = pd.concat(
                [data_funds[fund], benchmark_funds[benchmark]], axis=1
            ).dropna()
            kovarianz = np.cov(paired.iloc[:, 0], paired.iloc[:, 1])[0, 1]
            # ddof=1 (Stichprobe) passend zu np.cov
            varianz = np.var(paired.iloc[:, 1], ddof=1)

            results[fund][benchmark] = kovarianz / varianz

    return results


def calculate_alpha(data_funds_a, benchmark_funds_a, risk_free=RISK_FREE):
    results = {}
    betas = calculate_beta(data_funds_a, benchmark_funds_a)

    for fund in data_funds_a.columns:
        results[fund] = {}
        for bench in benchmark_funds_a.columns:
            rendite = data_funds_a[fund].mean() * TRADING_DAYS
            rendite_bench = benchmark_funds_a[bench].mean() * TRADING_DAYS
            beta = betas[fund][bench]
            alpha = rendite - (risk_free + beta * (rendite_bench - risk_free))

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
        after_trough = cumulative[trough_date:]
        recovery_date = after_trough[
            after_trough >= rolling_max[trough_date]
        ].first_valid_index()

        if recovery_date is None:
            results[fund] = "Nicht erholt"
        else:
            results[fund] = (recovery_date - trough_date).days

    return results
