import yfinance as yf
import pandas as pd

def load_data():
        
    # VOO = Vangaurd S&P 500 ETF Passive
    # IVV = ishares Core S&P 500 ETF Passive
    # FCNTX = Fidelity Contrafund Active
    # AGTHX = American Funds Growth Fund of Amercia Active

    tickers = ["VOO", "IVV", "FCNTX", "AGTHX"]

    # SPY = SPRD S&P 500 ETF Trust
    # IWB = iShares Russel 1000 ETF

    benchmarks = ["SPY", "IWB"]

    data = yf.download(tickers, start="2019-01-01", end="2026-01-01")

    bench_data = yf.download(benchmarks, start="2019-01-01", end= "2026-01-01")

    return data, bench_data

def daily_returns_tickers(data):
    return data["Close"].pct_change().dropna()

def daily_returns_benchmark(bench_data):
    return bench_data["Close"].pct_change().dropna() 



