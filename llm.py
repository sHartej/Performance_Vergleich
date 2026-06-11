"""KI-Modul (Google Gemini, kostenloser Tarif) fuer das Aktiv-vs-Passiv-Dashboard.

Zwei Funktionen:
  1. stream_analysis() - generiert eine kritische Aktiv-vs-Passiv-Bewertung
     aus den berechneten Kennzahlen (unterstuetzt Thema 6, Punkt 5).
  2. stream_chat() - beantwortet Nutzerfragen, ausschliesslich gestuetzt auf
     dieselben Kennzahlen.

Verwendet das google-genai SDK. Ein kostenloser API-Key ist unter
https://aistudio.google.com/apikey erhaeltlich (kein Zahlungsmittel noetig).
"""

import os
import time

from google import genai
from google.genai import errors, types

from config import PRODUCTS, METRIC_INFO

# Kostenloses Flash-Modell. Per Umgebungsvariable GEMINI_MODEL ueberschreibbar,
# falls das Standardmodell kein freies Kontingent hat (HTTP 429 / limit: 0).
# Alternativen mit Free-Tier: "gemini-2.0-flash", "gemini-flash-latest",
# "gemini-1.5-flash".
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")

# Bei Ueberlastung (503) oder Rate-Limit (429) werden diese Modelle der Reihe
# nach probiert.
FALLBACK_MODELS = [MODEL, "gemini-2.0-flash", "gemini-flash-latest"]

SYSTEM_INSTRUCTIONS = (
    "Du bist ein Finanzanalyst. Du vergleichst zwei aktiv und zwei "
    "passiv gemanagte Anlageprodukte anhand bereitgestellter Kennzahlen. "
    "Beziehe dich ausschliesslich auf die im Kontext gelieferten Zahlen und "
    "erfinde keine Werte. Wenn eine Information fehlt, sage das. Arbeite den "
    "Einfluss der Kosten (TER) auf die Netto-Performance explizit heraus und "
    "diskutiere kritisch, ob aktive Produkte ihren Kostennachteil rechtfertigen. "
    "Antworte praezise auf Deutsch."
)

ANALYSIS_PROMPT = (
    "Erstelle eine kritische Bewertung des Vergleichs aktiv vs. passiv. Gehe auf "
    "folgende Punkte ein:\n"
    "1. Welche Strategie schneidet netto (nach Kosten) besser ab und warum?\n"
    "2. Der Einfluss der TER auf die Netto-Performance - haben die aktiven "
    "Produkte ihren Kostennachteil durch messbaren Mehrwert kompensiert?\n"
    "3. Welche der Kennzahlen ist fuer diese Beurteilung am aussagekraeftigsten?\n"
    "4. Fuer welchen Anlegertyp ist welche Strategie geeignet?\n"
    "5. In welchen Marktphasen koennte aktives Management Vorteile haben?\n"
    "6. Welche Grenzen hat diese Analyse?\n"
    "Strukturiere die Antwort mit Markdown-Ueberschriften."
)


def build_context(results, benchmark):
    """Baut den Kennzahlen-Kontext fuer das LLM aus den Ergebnissen."""
    products = "\n".join(f"- {t}: {typ}" for t, typ in PRODUCTS.items())

    definitions = "\n".join(
        f"- {name} ({info['rolle']}): {info['definition']} "
        f"Interpretation: {info['interpretation']} Schwaeche: {info['schwaeche']}"
        for name, info in METRIC_INFO.items()
    )

    parts = [
        f"# Datengrundlage (Benchmark: {benchmark})",
        "## Produkte (aktiv/passiv)\n" + products,
        "## Kennzahlen NETTO (nach Kosten)\n"
        + results["metrics_net"].round(4).to_string(),
        "## Kennzahlen BRUTTO (vor Kosten)\n"
        + results["metrics_gross"].round(4).to_string(),
        "## Kosteneinfluss (TER, Brutto-/Netto-Rendite, Kostenabzug)\n"
        + results["cost_impact"].round(4).to_string(),
        "## Kennzahlen-Definitionen\n" + definitions,
    ]
    return "\n\n".join(parts)


def _client(api_key=None):
    key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get(
        "GOOGLE_API_KEY"
    )
    if not key:
        raise RuntimeError(
            "Kein GEMINI_API_KEY gefunden. Hole dir einen kostenlosen Schluessel "
            "unter https://aistudio.google.com/apikey und gib ihn im Dashboard ein "
            "oder setze die Umgebungsvariable GEMINI_API_KEY."
        )
    return genai.Client(api_key=key)


def _config(context, max_tokens):
    """GenerateContentConfig mit System-Instruktion + Kennzahlen-Kontext.

    thinking_budget=0 deaktiviert das interne "Denken" von Gemini 2.5 -
    dessen Tokens zaehlen sonst gegen max_output_tokens und schneiden die
    sichtbare Antwort mitten im Satz ab.
    """
    return types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTIONS + "\n\n" + context,
        max_output_tokens=max_tokens,
        temperature=0.3,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )


def _stream_with_fallback(client, contents, config):
    """Streamt mit automatischem Retry und Modell-Fallback bei 503/429.

    Probiert jedes Modell aus FALLBACK_MODELS bis zu zweimal (mit kurzer
    Wartezeit), bevor das naechste versucht wird. Erst wenn alle scheitern,
    wird der letzte Fehler geworfen.
    """
    last_error = None
    for model in FALLBACK_MODELS:
        for delay in (0, 4):
            if delay:
                time.sleep(delay)
            try:
                stream = client.models.generate_content_stream(
                    model=model, contents=contents, config=config
                )
                iterator = iter(stream)
                first = next(iterator, None)  # loest den Request aus
            except errors.APIError as exc:
                if exc.code in (429, 503):
                    last_error = exc
                    continue
                raise
            if first is not None and first.text:
                yield first.text
            for chunk in iterator:
                if chunk.text:
                    yield chunk.text
            return
    raise last_error


def stream_analysis(results, benchmark, api_key=None):
    """Generator: streamt die automatische Aktiv-vs-Passiv-Analyse als Text."""
    client = _client(api_key)
    config = _config(build_context(results, benchmark), max_tokens=8192)
    yield from _stream_with_fallback(client, ANALYSIS_PROMPT, config)


def stream_chat(results, benchmark, history, api_key=None):
    """Generator: streamt die Antwort auf eine Nutzerfrage (Chat).

    history: Liste von {"role": "user"|"assistant", "content": str}.
    Gemini erwartet die Rolle "model" statt "assistant".
    """
    client = _client(api_key)
    config = _config(build_context(results, benchmark), max_tokens=4096)
    contents = [
        {
            "role": "model" if m["role"] == "assistant" else "user",
            "parts": [{"text": m["content"]}],
        }
        for m in history
    ]
    yield from _stream_with_fallback(client, contents, config)
