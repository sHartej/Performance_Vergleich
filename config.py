"""Zentrale Konfiguration fuer den Performance-Vergleich (Thema 6).

Hier stehen die Anlageprodukte, die Benchmark, der Analysezeitraum sowie
die Kosten- (TER) und Kennzahlen-Metadaten. Dadurch sind Tickerlisten nicht
mehr ueber mehrere Dateien dupliziert.
"""

# --- Anlageprodukte: zwei aktiv, zwei passiv (gleiche Region/Anlageklasse/Waehrung) ---
# VOO   = Vanguard S&P 500 ETF            -> Passiv
# IVV   = iShares Core S&P 500 ETF        -> Passiv
# FCNTX = Fidelity Contrafund             -> Aktiv
# AGTHX = American Funds Growth Fund of America -> Aktiv
PRODUCTS = {
    "VOO": "Passiv",
    "IVV": "Passiv",
    "FCNTX": "Aktiv",
    "AGTHX": "Aktiv",
}

TICKERS = list(PRODUCTS.keys())

# Benchmarks (US Large-Cap): SPY = SPDR S&P 500, IWB = iShares Russell 1000
BENCHMARKS = ["SPY", "IWB"]

# Analysezeitraum (selbst gewaehlt)
START = "2019-01-01"
END = "2026-01-01"

# Risikofreier Zinssatz (annualisiert), z.B. ~US-Geldmarkt
RISK_FREE = 0.04

# Handelstage pro Jahr fuer die Annualisierung
TRADING_DAYS = 252

# Fallback-TER (jaehrlich, als Dezimalbruch), falls das Scraping fehlschlaegt.
# Quelle: oeffentliche Factsheets / Fondsprospekte (Naeherungswerte).
FALLBACK_TER = {
    "VOO": 0.0003,   # 0.03 %
    "IVV": 0.0003,   # 0.03 %
    "FCNTX": 0.0039,  # 0.39 %
    "AGTHX": 0.0061,  # 0.61 %
}

# --- Kennzahlen-Metadaten fuer das Dashboard (Definition, Interpretation, Schwaeche) ---
# Drei Kern-Kennzahlen decken die drei geforderten Perspektiven ab; zwei weitere
# Kennzahlen ergaenzen sie und gleichen deren Schwaechen aus.
METRIC_INFO = {
    "Sharpe Ratio": {
        "rolle": "Kern: risikoadjustierte Performance",
        "definition": "(Rendite - risikofreier Zins) / Gesamtvolatilitaet, annualisiert.",
        "interpretation": "Ueberrendite pro Einheit Gesamtrisiko. Hoeher = besser.",
        "schwaeche": "Bestraft Aufwaerts- wie Abwaertsschwankungen gleich und "
        "unterstellt normalverteilte Renditen.",
    },
    "Sortino Ratio": {
        "rolle": "Ergaenzung: korrigiert Schwaeche der Sharpe Ratio",
        "definition": "(Rendite - risikofreier Zins) / Abwaerts-Volatilitaet, annualisiert.",
        "interpretation": "Wie Sharpe, betrachtet aber nur das 'schlechte' Risiko "
        "(negative Renditen).",
        "schwaeche": "Ignoriert positive Schwankungen vollstaendig; instabil bei "
        "wenigen negativen Tagen.",
    },
    "Alpha": {
        "rolle": "Kern: relative Kennzahl vs. Benchmark",
        "definition": "Jensen-Alpha = R - [Rf + Beta * (R_benchmark - Rf)] (CAPM), annualisiert.",
        "interpretation": "Mehr-/Minderrendite gegenueber dem Marktrisiko. Genau hier "
        "muss sich aktives Management beweisen.",
        "schwaeche": "Haengt von Benchmark- und Beta-Schaetzung ab; sagt nichts ueber "
        "die Verlusttiefe.",
    },
    "Max Drawdown": {
        "rolle": "Kern: Risiko / Verlustanfaelligkeit",
        "definition": "Groesster prozentualer Rueckgang vom bisherigen Hoechststand bis zum Tief.",
        "interpretation": "Worst-Case-Verlust eines Buy-and-Hold-Anlegers. Naeher an 0 = besser.",
        "schwaeche": "Einzelereignis-Kennzahl; sagt nichts ueber die Haeufigkeit von "
        "Verlusten oder die Erholung.",
    },
    "Recovery (Tage)": {
        "rolle": "Ergaenzung: Stabilitaet / Erholungsfaehigkeit",
        "definition": "Anzahl Tage vom Drawdown-Tief bis zum Wiedererreichen des alten Hochs.",
        "interpretation": "Misst, wie schnell ein Produkt Verluste aufholt. Ergaenzt den "
        "Max Drawdown um die Zeitdimension.",
        "schwaeche": "Bezieht sich nur auf den groessten Drawdown; 'nicht erholt' ist "
        "schwer zu vergleichen.",
    },
}
