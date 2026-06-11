# Performance-Vergleich: Aktiv vs. Passiv (Thema 6)

Interaktives Streamlit-Dashboard, das die historische Performance von zwei
aktiv und zwei passiv gemanagten Anlageprodukten vergleicht – inklusive
Kosteneinfluss (TER) auf die Netto-Performance und einer KI-gestuetzten
Analyse (Google Gemini).

---

## 1. Schnellstart

### Voraussetzungen
- Python 3.13+ und [uv](https://docs.astral.sh/uv/) (Paket- und Umgebungsverwaltung)
- Internetverbindung (Kursdaten via yfinance, TER via Web Scraping)
- Kostenloser Gemini-API-Key fuer die KI-Analyse (optional, nur fuer Abschnitt 4)

### Installation
```powershell
uv sync
```

### Dashboard starten
```powershell
uv run streamlit run dashboard.py
```
Das Dashboard oeffnet sich im Browser (Standard: http://localhost:8501).

### Reine Konsolen-Analyse (ohne Dashboard)
```powershell
uv run python main.py
```

### Gemini-API-Key setzen (fuer KI-Analyse & Chat)
**Jedes Teammitglied braucht einen eigenen (kostenlosen) Key** – der Key wird
nie ins Repository committet, sondern nur lokal als Umgebungsvariable gesetzt.

1. Kostenlosen Key holen: https://aistudio.google.com/apikey (kein
   Zahlungsmittel noetig). Auf der Seite **"API-Schluessel erstellen"** klicken
   und den Key ueber das **Kopier-Symbol** in der Tabelle kopieren.
2. Entweder im Dashboard in die Seitenleiste eingeben, **oder** dauerhaft setzen:
   ```powershell
   setx GEMINI_API_KEY "dein-key-hier"
   ```
   Danach ein **neues** Terminal oeffnen (setx wirkt nur in neuen Fenstern;
   bei VS Code: VS Code komplett neu starten).
3. Pruefen, ob der Key ankommt (im neuen Terminal):
   ```powershell
   echo $env:GEMINI_API_KEY
   ```

Hinweis: Der kostenlose Tarif erlaubt ca. 10 Anfragen/Minute und ~250/Tag –
mehr als genug. Bei der Meldung "503 high demand" einfach kurz warten und
erneut klicken (der Code probiert automatisch Ersatzmodelle).

---

## 2. Projektstruktur

| Datei | Inhalt |
|---|---|
| `config.py` | Produkte (aktiv/passiv), Benchmark, Zeitraum, Risikozins, Fallback-TER, Kennzahlen-Metadaten |
| `data.py` | Laden der Kursdaten (yfinance), Berechnung der Tagesrenditen |
| `metrics.py` | Kennzahlen: Sharpe, Sortino, Beta, Alpha, Max Drawdown, Recovery |
| `scraper.py` | TER-Scraping (BeautifulSoup) mit Fallback-Werten |
| `main.py` | Analyse-Engine: Netto-Renditen, Kennzahlen-Tabellen, Kosteneinfluss |
| `dashboard.py` | Streamlit-Oberflaeche (Charts, Tabellen, KI-Analyse) |
| `llm.py` | KI-Modul (Gemini): automatische Analyse + Chat |

---

## 3. Anlageprodukte

| Ticker | Produkt | Typ |
|---|---|---|
| VOO | Vanguard S&P 500 ETF | Passiv |
| IVV | iShares Core S&P 500 ETF | Passiv |
| FCNTX | Fidelity Contrafund | Aktiv |
| AGTHX | American Funds Growth Fund of America | Aktiv |

Benchmark: SPY (SPDR S&P 500) bzw. IWB (iShares Russell 1000).
Vergleichbarkeit: gleiche Region (USA), Anlageklasse (US Large-Cap Aktien) und
Waehrung (USD). Zeitraum: 2019–2026 (selbst gewaehlt, im Dashboard anpassbar).

---

## 4. Gewaehlte Kennzahlen

Drei Kern-Kennzahlen decken die drei geforderten Perspektiven ab; zwei weitere
ergaenzen sie und gleichen deren Schwaechen aus.

| Kennzahl | Perspektive | Definition (kurz) | Schwaeche |
|---|---|---|---|
| **Sharpe Ratio** | Kern: risikoadjustiert | Ueberrendite / Gesamtvolatilitaet | bestraft Auf- und Abwaerts gleich |
| **Alpha (CAPM)** | Kern: relativ zur Benchmark | Mehrrendite ueber Marktrisiko | abhaengig von Benchmark/Beta |
| **Max Drawdown** | Kern: Risiko/Verlust | groesster Rueckgang vom Hoch | Einzelereignis, keine Haeufigkeit |
| Sortino Ratio | Ergaenzung | Ueberrendite / Abwaerts-Volatilitaet | ignoriert positive Schwankungen |
| Recovery (Tage) | Ergaenzung | Zeit bis zur Erholung | nur groesster Drawdown |

> **Hinweis zur Aufgabenstellung:** Thema 6 verlangt „genau drei" Metriken.
> Hier werden bewusst fuenf gezeigt (3 Kern + 2 Ergaenzung), weil sie sich
> gegenseitig ergaenzen. Bei Bedarf laesst sich das Modell auf die drei
> Kern-Kennzahlen reduzieren – mit dem Professor abstimmen.

---

## 5. Erfuellung der Aufgabenstellung (Thema 6)

1. **Datensammlung** – 4 vergleichbare Produkte + TER (gescraped, mit Fallback).
2. **Kennzahlen-Auswahl** – Definition/Interpretation/Schwaeche je Kennzahl
   (im Dashboard unter Abschnitt 2 aufklappbar).
3. **Implementierung & Vergleich** – Kennzahlen in Python, Brutto- und
   **Netto-Renditen** (nach TER), expliziter Kosteneinfluss.
4. **Streamlit-Dashboard** – Wertentwicklung, Kennzahlen-Tabelle,
   Kosteneinfluss-Visualisierung, KI-Analyse.
5. **Praesentation & Diskussion** – siehe naechster Abschnitt.

---

## 6. Talking Points fuer die Praesentation (Punkt 5)

**Welche Strategie schneidet besser ab?**
Im Zeitraum 2019–2026 schlugen die aktiven Fonds netto im Schnitt die passiven
(ca. 18,7 % vs. 17,9 % p. a.). Aber: differenziert betrachten – FCNTX zeigt
positives Alpha (+1,5 %), AGTHX leicht negatives (−0,7 %).

**Haben die aktiven Produkte ihren Kostennachteil gerechtfertigt?**
Die TER der aktiven Fonds (~0,6–0,7 %) ist deutlich hoeher als die der
passiven (~0,03 %). FCNTX hat diesen Nachteil durch Mehrwert kompensiert,
AGTHX nicht. Der Kosteneffekt ist im Dashboard (Abschnitt 3, Brutto vs. Netto)
direkt ablesbar.

**Welche Kennzahl ist am aussagekraeftigsten?**
Fuer den Vergleich aktiv vs. passiv ist **Alpha** zentral, weil es genau die
risikoadjustierte Mehrrendite gegenueber dem Markt misst – dort muss sich
aktives Management beweisen. Die Sharpe Ratio ergaenzt um die Gesamt-Effizienz.

**Fuer welchen Anlegertyp?**
- Passiv (VOO/IVV): kostenbewusste, langfristige Buy-and-Hold-Anleger.
- Aktiv (FCNTX): Anleger, die an Managerqualitaet glauben und hoehere Kosten
  fuer potenziellen Mehrwert akzeptieren.

**Wann kann aktives Management Vorteile haben?**
Tendenziell in ineffizienten Marktphasen, bei hoher Streuung der Einzelwerte
oder in Abschwuengen (aktives Risikomanagement).

**Grenzen der Analyse (wichtig – ehrlich nennen):**
- FCNTX/AGTHX sind **Growth**-Fonds, die Benchmark (S&P 500) ist **Blend** –
  ein Teil der Outperformance ist ein Growth-Tilt, nicht reine Managerleistung.
- TER wird vereinfacht gleichmaessig auf Handelstage verteilt (ter/252).
- Vergangenheitsdaten; keine Aussage ueber die Zukunft.
- Ergebnis haengt vom gewaehlten Zeitraum ab (im Dashboard testbar).

---

## 7. Hinweise / Bekannte Einschraenkungen

- Das TER-Scraping haengt vom HTML von Yahoo Finance ab; faellt es aus, greifen
  die Fallback-Werte aus `config.py`.
- Die KI-Analyse nutzt den kostenlosen Gemini-Tarif (Rate Limits beachten).
- Ohne API-Key funktionieren die Abschnitte 1–3 vollstaendig; nur Abschnitt 4
  (KI) benoetigt den Key.
