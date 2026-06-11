import requests
from bs4 import BeautifulSoup

from config import TICKERS, FALLBACK_TER


def _parse_ter(text):
    """Wandelt einen TER-Text wie '0.03%' in einen Dezimalbruch (0.0003) um."""
    if not text:
        return None
    text = text.strip().replace("%", "")
    try:
        return float(text) / 100
    except ValueError:
        return None


def scrape_ter(ticker):
    """Versucht, die Total Expense Ratio (TER) von Yahoo Finance zu scrapen.

    Gibt einen Dezimalbruch zurueck (z.B. 0.0003 fuer 0.03 %) oder None,
    falls die Seite nicht erreichbar ist oder das Feld fehlt.
    """
    url = f"https://finance.yahoo.com/quote/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # ETFs nutzen "Expense Ratio (net)", Fonds "Expense Ratio"
    label = soup.find("span", title="Expense Ratio (net)") or soup.find(
        "span", title="Expense Ratio"
    )
    if label is None:
        return None

    value = label.find_next_sibling("span")
    if value is None:
        return None

    return _parse_ter(value.text)


def get_all_ter(tickers=TICKERS):
    """Holt die TER aller Produkte. Faellt bei Fehlern auf bekannte Werte zurueck.

    Rueckgabe: dict {ticker: jaehrliche TER als Dezimalbruch}.
    """
    ter_data = {}
    for ticker in tickers:
        scraped = scrape_ter(ticker)
        if scraped is None:
            ter_data[ticker] = FALLBACK_TER.get(ticker)
        else:
            ter_data[ticker] = scraped
    return ter_data


if __name__ == "__main__":
    for ticker, ter in get_all_ter().items():
        print(f"{ticker}: {ter:.4%}" if ter is not None else f"{ticker}: n/a")
