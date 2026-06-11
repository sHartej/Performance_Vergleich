"""Interaktives Streamlit-Dashboard: Performance-Vergleich Aktiv vs. Passiv.

Erfuellt Thema 6, Punkt 4:
- Visualisierung der historischen Wertentwicklung
- uebersichtliche Darstellung der gewaehlten Kennzahlen
- nachvollziehbare Visualisierung des Kosteneinflusses (brutto vs. netto)
"""

import datetime as dt
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from config import BENCHMARKS, PRODUCTS, START, END, RISK_FREE, METRIC_INFO
import main
import llm

st.set_page_config(page_title="Aktiv vs. Passiv", layout="wide")


@st.cache_data(show_spinner="Lade Kursdaten und berechne Kennzahlen ...")
def get_results(benchmark, start, end, risk_free):
    return main.run_analysis(
        benchmark=benchmark, start=start, end=end, risk_free=risk_free
    )


# --------------------------------------------------------------------------- #
# Sidebar: Parameter
# --------------------------------------------------------------------------- #
st.sidebar.header("Parameter")

benchmark = st.sidebar.selectbox("Benchmark", BENCHMARKS, index=0)

start_date = st.sidebar.date_input(
    "Startdatum", value=dt.date.fromisoformat(START)
)
end_date = st.sidebar.date_input("Enddatum", value=dt.date.fromisoformat(END))

risk_free = st.sidebar.number_input(
    "Risikofreier Zins (annualisiert)",
    min_value=0.0,
    max_value=0.15,
    value=float(RISK_FREE),
    step=0.005,
    format="%.3f",
)

view = st.sidebar.radio(
    "Renditebasis", ["Netto (nach Kosten)", "Brutto (vor Kosten)"], index=0
)
net_view = view.startswith("Netto")

st.sidebar.divider()
st.sidebar.subheader("KI-Analyse (Gemini)")
env_key = os.environ.get("GEMINI_API_KEY", "")
if env_key:
    st.sidebar.success("API-Key aus Umgebungsvariable geladen.")
    api_key = env_key
else:
    api_key = st.sidebar.text_input(
        "GEMINI_API_KEY",
        type="password",
        help="Kostenloser Schluessel: https://aistudio.google.com/apikey",
    )

st.sidebar.caption(
    "Produkte: "
    + ", ".join(f"{t} ({typ})" for t, typ in PRODUCTS.items())
)

results = get_results(
    benchmark, start_date.isoformat(), end_date.isoformat(), risk_free
)

growth = results["growth_net"] if net_view else results["growth_gross"]
metrics = results["metrics_net"] if net_view else results["metrics_gross"]

# Farbe je Typ (aktiv/passiv) fuer die Charts
color_map = {
    t: ("#d62728" if PRODUCTS[t] == "Aktiv" else "#1f77b4") for t in PRODUCTS
}

# --------------------------------------------------------------------------- #
# Kopf
# --------------------------------------------------------------------------- #
st.title("Performance-Vergleich: Aktiv vs. Passiv")
st.caption(
    f"Benchmark: {benchmark}  |  Zeitraum: {start_date} bis {end_date}  |  "
    f"Ansicht: {view}"
)

# --------------------------------------------------------------------------- #
# 1) Historische Wertentwicklung
# --------------------------------------------------------------------------- #
st.subheader("1. Historische Wertentwicklung")
st.caption("Wert eines mit 1,00 gestarteten Investments.")

fig = go.Figure()
for ticker in growth.columns:
    fig.add_trace(
        go.Scatter(
            x=growth.index,
            y=growth[ticker],
            name=f"{ticker} ({PRODUCTS[ticker]})",
            line=dict(color=color_map[ticker]),
        )
    )
fig.update_layout(
    yaxis_title="Wachstum von 1,00",
    xaxis_title="Datum",
    legend_title="Produkt",
    height=450,
)
st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------------------------- #
# 2) Kennzahlen-Uebersicht
# --------------------------------------------------------------------------- #
st.subheader("2. Kennzahlen im Vergleich")

fmt = {
    "Sharpe Ratio": "{:.2f}",
    "Sortino Ratio": "{:.2f}",
    "Alpha": "{:.2%}",
    "Max Drawdown": "{:.2f}%",
}
st.dataframe(
    metrics.style.format(fmt, na_rep="-"),
    use_container_width=True,
)

# Aggregat: Mittelwert je Typ (aktiv vs. passiv)
numeric_cols = ["Sharpe Ratio", "Sortino Ratio", "Alpha", "Max Drawdown"]
agg = metrics.groupby("Typ")[numeric_cols].mean()
st.caption("Durchschnitt je Strategie (aktiv vs. passiv):")
st.dataframe(agg.style.format("{:.3f}"), use_container_width=True)

with st.expander("Warum diese Kennzahlen? (Definition, Interpretation, Schwaeche)"):
    for name, info in METRIC_INFO.items():
        st.markdown(
            f"**{name}** — *{info['rolle']}*  \n"
            f"- Definition: {info['definition']}  \n"
            f"- Interpretation: {info['interpretation']}  \n"
            f"- Schwaeche: {info['schwaeche']}"
        )
    st.info(
        "Drei Kern-Kennzahlen (Sharpe, Alpha, Max Drawdown) decken die drei "
        "geforderten Perspektiven ab. Sortino und Recovery ergaenzen sie und "
        "gleichen deren Schwaechen aus."
    )

# --------------------------------------------------------------------------- #
# 3) Einfluss der Kosten auf die Netto-Performance
# --------------------------------------------------------------------------- #
st.subheader("3. Einfluss der Kosten (TER) auf die Performance")

cost = results["cost_impact"].copy()

c1, c2 = st.columns([3, 2])

with c1:
    bar = go.Figure()
    bar.add_trace(
        go.Bar(
            x=cost.index,
            y=cost["Rendite brutto"],
            name="Brutto (vor Kosten)",
            marker_color="#aec7e8",
        )
    )
    bar.add_trace(
        go.Bar(
            x=cost.index,
            y=cost["Rendite netto"],
            name="Netto (nach Kosten)",
            marker_color="#1f77b4",
        )
    )
    bar.update_layout(
        barmode="group",
        yaxis_title="Annualisierte Rendite",
        xaxis_title="Produkt",
        height=400,
        legend_title="",
    )
    bar.update_yaxes(tickformat=".1%")
    st.plotly_chart(bar, use_container_width=True)

with c2:
    cost_fmt = cost.copy()
    st.dataframe(
        cost_fmt.style.format(
            {
                "TER": "{:.2%}",
                "Rendite brutto": "{:.2%}",
                "Rendite netto": "{:.2%}",
                "Kostenabzug": "{:.2%}",
            }
        ),
        use_container_width=True,
    )

# Direkter Aktiv-vs-Passiv-Vergleich der durchschnittlichen TER und Netto-Rendite
cost_by_type = cost.groupby("Typ")[["TER", "Rendite netto"]].mean()
colA, colB = st.columns(2)
with colA:
    st.metric(
        "Durchschnittliche TER",
        f"{cost_by_type.loc['Aktiv', 'TER']:.2%} (aktiv)",
        f"{cost_by_type.loc['Aktiv', 'TER'] - cost_by_type.loc['Passiv', 'TER']:.2%} vs. passiv",
        delta_color="inverse",
    )
with colB:
    st.metric(
        "Durchschnittliche Netto-Rendite",
        f"{cost_by_type.loc['Aktiv', 'Rendite netto']:.2%} (aktiv)",
        f"{cost_by_type.loc['Aktiv', 'Rendite netto'] - cost_by_type.loc['Passiv', 'Rendite netto']:.2%} vs. passiv",
    )

st.caption(
    "Kernfrage: Rechtfertigt der Mehrwert aktiver Produkte ihren Kostennachteil? "
    "Vergleiche die Netto-Rendite und das Alpha der aktiven mit den passiven Produkten."
)

# --------------------------------------------------------------------------- #
# 4) KI-gestuetzte Analyse & Chat (Claude)
# --------------------------------------------------------------------------- #
st.subheader("4. KI-gestuetzte Analyse (Gemini)")

if not api_key:
    st.info(
        "Gib in der Seitenleiste einen (kostenlosen) GEMINI_API_KEY ein, um die "
        "automatische Analyse und den Chat zu nutzen. Schluessel erhaeltlich unter "
        "https://aistudio.google.com/apikey"
    )
else:
    # 4a) Automatische kritische Analyse
    if st.button("Kritische Aktiv-vs-Passiv-Analyse generieren"):
        try:
            st.write_stream(
                llm.stream_analysis(results, benchmark, api_key=api_key)
            )
        except Exception as exc:  # API-/Netzwerkfehler nutzerfreundlich zeigen
            st.error(f"KI-Analyse fehlgeschlagen: {exc}")

    # 4b) Chat, der auf denselben Kennzahlen basiert
    st.markdown("**Fragen zu den Kennzahlen**")
    if "chat" not in st.session_state:
        st.session_state.chat = []

    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("z. B. Warum hat FCNTX die passiven Produkte geschlagen?")
    if prompt:
        st.session_state.chat.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                answer = st.write_stream(
                    llm.stream_chat(
                        results, benchmark, st.session_state.chat, api_key=api_key
                    )
                )
                st.session_state.chat.append(
                    {"role": "assistant", "content": answer}
                )
            except Exception as exc:
                st.error(f"Chat fehlgeschlagen: {exc}")
                st.session_state.chat.pop()  # fehlgeschlagene Nutzerfrage zuruecknehmen
