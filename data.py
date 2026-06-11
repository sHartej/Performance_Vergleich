import yfinance as yf

from config import TICKERS, BENCHMARKS, START, END


def load_data(tickers=TICKERS, benchmarks=BENCHMARKS, start=START, end=END):
    """Laedt historische Kursdaten der Produkte und der Benchmarks via yfinance.

    auto_adjust=True liefert bereits um Dividenden/Splits bereinigte Kurse,
    sodass die Renditen die tatsaechliche Wertentwicklung abbilden.
    """
    data = yf.download(tickers, start=start, end=end, auto_adjust=True)
    bench_data = yf.download(benchmarks, start=start, end=end, auto_adjust=True)

    return data, bench_data


def daily_returns_tickers(data):
    return data["Close"].pct_change().dropna()


def daily_returns_benchmark(bench_data):
    return bench_data["Close"].pct_change().dropna()
