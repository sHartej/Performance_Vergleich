"""Analyse-Engine fuer den Performance-Vergleich Aktiv vs. Passiv (Thema 6).

Dieses Modul stellt Funktionen bereit, die sowohl von der CLI (unten im
__main__-Block) als auch vom Streamlit-Dashboard genutzt werden. Beim reinen
Import werden KEINE Daten geladen (kein Code auf Modulebene), damit das
Dashboard nicht bei jedem Rerun das gesamte Netzwerk anstoesst.
"""

import pandas as pd

from config import PRODUCTS, TRADING_DAYS, RISK_FREE
from data import load_data, daily_returns_tickers, daily_returns_benchmark
from metrics import (
    sharpe_ratio,
    sortino_ratio,
    calculate_alpha,
    calculate_max_drawdown,
    calculate_recovery_period,
)
from scraper import get_all_ter


def apply_costs(returns, ter):
    """Zieht die anteilige taegliche TER von den Brutto-Renditen ab.

    TER ist eine jaehrliche Gebuehr; vereinfachend wird sie gleichmaessig auf
    alle Handelstage verteilt (ter / 252 pro Tag). Ergebnis = Netto-Renditen.
    """
    daily_cost = pd.Series(ter) / TRADING_DAYS
    return returns.subtract(daily_cost, axis=1)


def cumulative_growth(returns):
    """Wertentwicklung eines mit 1.0 gestarteten Investments (kumulierte Rendite)."""
    return (1 + returns).cumprod()


def metrics_table(returns, bench_returns, benchmark, risk_free=RISK_FREE):
    """Baut eine einheitliche Kennzahlen-Tabelle (Index = Produkt)."""
    alpha = calculate_alpha(returns, bench_returns, risk_free)
    recovery = calculate_recovery_period(returns)

    table = pd.DataFrame(index=returns.columns)
    table["Typ"] = [PRODUCTS.get(t, "?") for t in returns.columns]
    table["Sharpe Ratio"] = sharpe_ratio(returns, risk_free)
    table["Sortino Ratio"] = sortino_ratio(returns, risk_free)
    table["Alpha"] = pd.Series({f: alpha[f][benchmark] for f in returns.columns})
    table["Max Drawdown"] = calculate_max_drawdown(returns)
    table["Recovery (Tage)"] = pd.Series(recovery)
    return table


def annualized_return(returns):
    """Annualisierte Durchschnittsrendite je Produkt."""
    return returns.mean() * TRADING_DAYS


def cost_impact_table(gross_returns, net_returns, ter):
    """Stellt den Einfluss der Kosten auf die Netto-Performance explizit dar."""
    gross = annualized_return(gross_returns)
    net = annualized_return(net_returns)
    table = pd.DataFrame(
        {
            "Typ": pd.Series({t: PRODUCTS.get(t, "?") for t in gross.index}),
            "TER": pd.Series(ter),
            "Rendite brutto": gross,
            "Rendite netto": net,
            "Kostenabzug": gross - net,
        }
    )
    return table


def run_analysis(benchmark, start=None, end=None, risk_free=RISK_FREE):
    """Fuehrt die komplette Analyse aus und gibt alle Ergebnisse als dict zurueck."""
    if start is not None or end is not None:
        from config import START, END

        data, bench_data = load_data(start=start or START, end=end or END)
    else:
        data, bench_data = load_data()

    gross_returns = daily_returns_tickers(data)
    bench_returns = daily_returns_benchmark(bench_data)

    ter = get_all_ter()
    net_returns = apply_costs(gross_returns, ter)

    return {
        "ter": ter,
        "gross_returns": gross_returns,
        "net_returns": net_returns,
        "bench_returns": bench_returns,
        "metrics_gross": metrics_table(gross_returns, bench_returns, benchmark, risk_free),
        "metrics_net": metrics_table(net_returns, bench_returns, benchmark, risk_free),
        "cost_impact": cost_impact_table(gross_returns, net_returns, ter),
        "growth_gross": cumulative_growth(gross_returns),
        "growth_net": cumulative_growth(net_returns),
    }


if __name__ == "__main__":
    from config import BENCHMARKS

    results = run_analysis(benchmark=BENCHMARKS[0])

    print("\n=== TER (jaehrlich) ===")
    for ticker, ter in results["ter"].items():
        print(f"  {ticker}: {ter:.4%}")

    print("\n=== Kennzahlen (netto, nach Kosten) ===")
    print(results["metrics_net"].round(4).to_string())

    print("\n=== Kosteneinfluss auf die Netto-Performance ===")
    print(results["cost_impact"].round(4).to_string())
