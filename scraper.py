import requests
from bs4 import BeautifulSoup

def scrape_ter(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    # ETFs use "Expense Ratio (net)", mutual funds use "Expense Ratio"
    label = soup.find("span", title="Expense Ratio (net)") or \
            soup.find("span", title="Expense Ratio")
    
    if label is None:
        return None
    
    ter_value = label.find_next_sibling("span", class_="value yf-13utneb")
    
    return ter_value.text

def get_all_ter():
    tickers = ["VOO", "IVV", "FCNTX", "AGTHX"]
    ter_data = {}
    for ticker in tickers:
        ter_data[ticker] = scrape_ter(ticker)
        print(f"{ticker}: {ter_data[ticker]}")
    return ter_data
