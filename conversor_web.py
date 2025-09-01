import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder
from pathlib import Path
import random

# ---------- CONFIG ----------
st.set_page_config(
    page_title="Conversor de Moedas",
    page_icon="💱",
    layout="centered"
)

# ---------- IDIOMAS ----------
IDIOMAS = {
    "pt": {
        "lang_label": "Escolha o idioma",
        "title": "Conversor de Moedas Inteligente",
        "subtitle": "Conectado ao Banco Central Europeu • Atualizado diariamente às 16:00 CET",
        "tab_api": "API BCE",
        "tab_csv": "CSV offline",
        "amount": "Digite o valor",
        "from": "Moeda de origem",
        "to": "Moeda de destino",
        "convert": "🔄 Converter",
        "result": "Resultado",
        "history": "🕒 Histórico de conversões",
        "range": "Escolha o intervalo de datas",
        "show_chart": "📊 Mostrar gráfico histórico",
        "source": "📊 Dados do BCE (via Frankfurter). Atualizados às 16:00 CET.",
        "error_api": "Erro ao conectar com a API.",
        "no_data": "Sem dados para o período escolhido.",
        "invalid_range": "⛔ Intervalo inválido: a data inicial não pode ser maior que a final.",
        "csv_hint": "Arraste um arquivo cambios.csv ou deixe na mesma pasta.",
        "reload": "⟳ Recarregar CSV",
        "filter": "Filtrar moeda...",
        "order": "Ordenar por",
        "order_currency": "Moeda",
        "order_rate": "Taxa",
        "ready_csv": "Pronto quando o CSV carregar.",
        "curiosity": "🎯 Curiosidade do dia",
        "tip": "💡 Dica financeira",
    },
    "es": {
        "lang_label": "Elige el idioma",
        "title": "Conversor de Monedas Inteligente",
        "subtitle": "Conectado al Banco Central Europeo • Actualizado diariamente a las 16:00 CET",
        "tab_api": "API BCE",
        "tab_csv": "CSV offline",
        "amount": "Introduce el valor",
        "from": "Moneda de origen",
        "to": "Moneda de destino",
        "convert": "🔄 Convertir",
        "result": "Resultado",
        "history": "🕒 Historial de conversiones",
        "range": "Selecciona el rango de fechas",
        "show_chart": "📊 Mostrar gráfico histórico",
        "source": "📊 Datos del BCE (vía Frankfurter). Actualizados a las 16:00 CET.",
        "error_api": "No se pudo conectar con la API.",
        "no_data": "Sin datos para el período elegido.",
        "invalid_range": "⛔ Rango inválido: la fecha inicial no puede ser mayor que la final.",
        "csv_hint": "Arrastra un archivo cambios.csv o déjalo en la misma carpeta.",
        "reload": "⟳ Recargar CSV",
        "filter": "Filtrar moneda...",
        "order": "Ordenar por",
        "order_currency": "Moneda",
        "order_rate": "Tasa",
        "ready_csv": "Listo cuando el CSV cargue.",
        "curiosity": "🎯 Curiosidad del día",
        "tip": "💡 Consejo financiero",
    },
    "en": {
        "lang_label": "Choose language",
        "title": "Smart Currency Converter",
        "subtitle": "Connected to the ECB • Updated daily at 16:00 CET",
        "tab_api": "ECB API",
        "tab_csv": "CSV offline",
        "amount": "Enter amount",
        "from": "From currency",
        "to": "To currency",
        "convert": "🔄 Convert",
        "result": "Result",
        "history": "🕒 Conversion history",
        "range": "Select date range",
        "show_chart": "📊 Show historical chart",
        "source": "📊 Data from ECB (via Frankfurter). Updated at 16:00 CET.",
        "error_api": "Could not connect to the API.",
        "no_data": "No data for the selected period.",
        "invalid_range": "⛔ Invalid range: start date cannot be after end date.",
        "csv_hint": "Drop a cambios.csv file or keep it in the same folder.",
        "reload": "⟳ Reload CSV",
        "filter": "Filter currency...",
        "order": "Order by",
        "order_currency": "Currency",
        "order_rate": "Rate",
        "ready_csv": "Ready once the CSV loads.",
        "curiosity": "🎯 Curiosity of the day",
        "tip": "💡 Tip",
    }
}

lang = st.selectbox("🌍 " + IDIOMAS["pt"]["lang_label"] + " / " +
                    IDIOMAS["es"]["lang_label"] + " / " +
                    IDIOMAS["en"]["lang_label"], ["pt", "es", "en"], index=0)
T = IDIOMAS[lang]

SYMB = {"EUR": "€", "USD": "$", "BRL": "R$"}

DICAS = {
    "BRL": {
        "pt": ["Compare taxas entre bancos antes de trocar reais.", "O real pode se desvalorizar em anos eleitorais."],
        "es": ["Compara tasas entre bancos antes de cambiar reales.", "El real puede depreciarse en años electorales."],
        "en": ["Compare bank rates before converting BRL.", "BRL may weaken in election years."]
    },
    "USD": {
        "pt": ["O dólar é aceito em muitos países.", "As decisões da Fed afetam o valor global."],
        "es": ["El dólar es aceptado en muchos países.", "Las decisiones de la Fed mueven el valor global."],
        "en": ["Widely accepted worldwide.", "Fed decisions influence global value."]
    },
    "EUR": {
        "pt": ["Estável, mas sensível ao BCE.", "Segunda moeda mais usada em reservas."],
        "es": ["Estable pero sensible al BCE.", "Segunda moneda en reservas."],
        "en": ["Stable but sensitive to ECB.", "Second most used in reserves."]
    }
}

# ---------- STATE ----------
if "hist" not in st.session_state:
    st.session_state.hist = []

if "seed_curio" not in st.session_state:
    st.session_state.seed_curio = datetime.now().strftime("%Y-%m-%d")

# ---------- HELPERS ----------
@st.cache_data
def frank_latest(amount: float, origem: str, destino: str):
    url = f"https://api.frankfurter.app/latest?amount={amount}&from={origem}&to={destino}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    return r.json()

@st.cache_data
def frank_series(start: date, end: date, origem: str, destino: str):
    url = f"https://api.frankfurter.app/{start}..{end}?from={origem}&to={destino}"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json().get("rates", {})
    fechas = sorted(data.keys())
    if not fechas:
        return pd.DataFrame(columns=["date", "rate"])
    rows = [{"date": pd.to_datetime(d), "rate": data[d][destino]} for d in fechas]
    return pd.DataFrame(rows)

@st.cache_data
def load_csv(file_or_path):
    if file_or_path is None:
        p = Path("cambios.csv")
        if not p.exists():
            return pd.DataFrame()
        file_or_path = str(p)
    # separador automático; tolera ',' ';' e espaços
    df = pd.read_csv(file_or_path, sep=None, engine="python")
    # normaliza nomes de coluna comuns
    cols = {c.lower().strip(): c for c in df.columns}
    moeda_col = cols.get("moeda") or cols.get("par") or cols.get("moneda") or list(df.columns)[0]
    taxa_col  = cols.get("taxa")  or cols.get("cambio") or cols.get("rate")   or list(df.columns)[1]
    df = df.rename(columns={moeda_col: "Moeda", taxa_col: "Taxa"})
    df["Moeda"] = df["Moeda"].astype(str).str.upper().str.strip()
    df["Taxa"] = pd.to_numeric(df["Taxa"], errors="coerce")
    df = df.dropna(subset=["Taxa"]).reset_index(drop=True)
    return df

def curiosity_for(currency: str):
    archivo = {"BRL": "curiosidades_br.txt", "EUR": "curiosidades_es.txt", "USD": "curiosities_us.txt"}.get(currency, "")
    try:
        lines = Path(archivo).read_text(encoding="utf-8").splitlines()
        lines = [x.strip() for x in lines if x.strip()]
        if not lines:
            return ""
        random.seed(st.session_state.seed_curio + currency)
        return random.choice(lines)
    except Exception:
        return ""

def tip_for(currency: str, lang: str):
    return random.choice(DICAS.get(currency, {}).get(lang, [])) if DICAS.get(currency) else ""

def metric_value(sym, value, code):
    if sym:
        return f"{sym} {value:,.2f} {code}"
    return f"{value:,.2f} {code}"

# ---------- HEADER ----------
st.title(T["title"])
st.caption(T["subtitle"])

tab_api, tab_csv = st.tabs([T["tab_api"], T["tab_csv"]])

# ---------- TAB API ----------
with tab_api:
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        amount = st.number_input(T["amount"], min_value=0.0, value=5.0, step=1.0, format="%.2f")
        origem = st.selectbox(T["from"], ["EUR", "USD", "BRL"], index=0)
    with col2:
        destino = st.selectbox(T["to"], ["EUR", "USD", "BRL"], index=2)

    if st.button(T["convert"]):
        try:
            if origem == destino:
                result = amount
            else:
                data = frank_latest(amount, origem, destino)
                result = float(data["rates"][destino])
            st.metric(T["result"], metric_value(SYMB.get(destino, ""), result, destino),
                      delta=metric_value(SYMB.get(origem, ""), amount, origem))
            curio = curiosity_for(destino)
            if curio:
                st.info(f'{T["curiosity"]}: {curio}')
            dica = tip_for(destino, lang)
            if dica:
                st.warning(f'{T["tip"]}: {dica}')
            st.session_state.hist.append(
                f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | '
                f'{metric_value(SYMB.get(origem,""), amount, origem)} → {metric_value(SYMB.get(destino,""), result, destino)}'
            )
        except Exception:
            st.error(T["error_api"])

    if st.session_state.hist:
        st.subheader(T["history"])
        # tabela bonita com AgGrid
        hist_df = pd.DataFrame({"Registro": list(reversed(st.session_state.hist[-50:]))})
        gb = GridOptionsBuilder.from_dataframe(hist_df)
        gb.configure_grid_options(domLayout='autoHeight')
        gb.configure_default_column(resizable=True, sortable=True, filter=True)
        AgGrid(hist_df, gridOptions=gb.build(), theme="balham", fit_columns_on_grid_load=True)

    st.divider()
    st.subheader(T["show_chart"])
    start, end = st.date_input(T["range"], [date(2024, 1, 1), date(2024, 12, 31)])
    if start > end:
        st.error(T["invalid_range"])
    else:
        if st.button(T["show_chart"] + " ▶"):
            try:
                df = frank_series(start, end, origem, destino)
                if df.empty:
                    st.warning(T["no_data"])
                else:
                    fig = px.line(df, x="date", y="rate", markers=True,
                                  labels={"date": "Data" if lang=="pt" else "Fecha" if lang=="es" else "Date",
                                          "rate": "Taxa de câmbio" if lang=="pt" else "Tasa de cambio" if lang=="es" else "Exchange rate"},
                                  title=f"{origem} → {destino}")
                    fig.update_layout(height=380, margin=dict(l=20, r=20, t=60, b=20))
                    st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.error(T["error_api"])

    st.caption(T["source"])

# ---------- TAB CSV ----------
with tab_csv:
    st.divider()
    st.write("**" + T["csv_hint"] + "**")
    up = st.file_uploader("cambios.csv", type=["csv"], accept_multiple_files=False, label_visibility="collapsed")
    colf, colr = st.columns([3,1])
    with colf:
        filtro = st.text_input(T["filter"])
    with colr:
        ord_opt = st.selectbox(T["order"], [T["order_currency"], T["order_rate"]], index=0)
    if st.button(T["reload"]):
        st.experimental_rerun()

    df = load_csv(up)
    if df.empty:
        st.info(T["ready_csv"])
    else:
        if filtro:
            df = df[df["Moeda"].str.contains(filtro.strip(), case=False, na=False)]
        df = df.sort_values("Moeda" if ord_opt == T["order_currency"] else "Taxa")
        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_grid_options(domLayout='autoHeight')
        gb.configure_default_column(resizable=True, sortable=True, filter=True)
        AgGrid(df, gridOptions=gb.build(), theme="balham", fit_columns_on_grid_load=True)






