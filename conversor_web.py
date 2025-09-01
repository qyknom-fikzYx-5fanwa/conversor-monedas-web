import streamlit as st
import requests
from datetime import datetime, date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random
from pathlib import Path

# TEM QUE SER O PRIMEIRO
st.set_page_config(page_title="Conversor de Moedas", layout="centered")

# 🌐 Idioma
idioma_actual = st.selectbox("🌍 Elige el idioma / Escolha o idioma / Choose language", ["pt", "es", "en"], index=0)

idiomas = {
    "es": {
        "titulo": "Conversor de Monedas Inteligente",
        "descripcion": "Conectado al Banco Central Europeo • Actualizado diariamente a las 16:00 CET",
        "valor": "Introduce el valor",
        "de": "Moneda de origen",
        "para": "Moneda de destino",
        "convertir": "🔄 Convertir",
        "resultado": "Resultado",
        "grafico": "📈 Mostrar gráfico histórico",
        "rango": "Selecciona el rango de fechas",
        "historial": "🕒 Historial de conversiones",
        "fuente": "📊 Datos del Banco Central Europeo (vía Frankfurter). Actualizados a las 16:00 CET.",
        "error_api": "No se pudo conectar con la API.",
        "error_grafico": "No se pudo generar el gráfico.",
        "mostrar_graf": "📊 Mostrar gráfico histórico"
    },
    "pt": {
        "titulo": "Guia de câmbio pessoal para cada viagem ao Brasil",
        "descripcion": "Conectado ao Banco Central Europeu • Atualizado diariamente às 16:00 CET",
        "valor": "Digite o valor",
        "de": "Moeda de origem",
        "para": "Moeda de destino",
        "convertir": "🔄 Converter",
        "resultado": "Resultado",
        "grafico": "📈 Mostrar gráfico histórico",
        "rango": "Escolha o intervalo de datas",
        "historial": "🕒 Histórico de conversões",
        "fuente": "📊 Dados do Banco Central Europeu (via Frankfurter). Atualizados às 16:00 CET.",
        "error_api": "Erro ao conectar com a API.",
        "error_grafico": "Não foi possível gerar o gráfico.",
        "mostrar_graf": "📊 Mostrar gráfico histórico"
    },
    "en": {
        "titulo": "Smart Currency Converter",
        "descripcion": "Connected to the European Central Bank • Updated daily at 16:00 CET",
        "valor": "Enter amount",
        "de": "From currency",
        "para": "To currency",
        "convertir": "🔄 Convert",
        "resultado": "Result",
        "grafico": "📈 Show historical chart",
        "rango": "Select date range",
        "historial": "🕒 Conversion history",
        "fuente": "📊 Data from the European Central Bank (via Frankfurter). Updated at 16:00 CET.",
        "error_api": "Could not connect to the API.",
        "error_grafico": "Could not generate the chart.",
        "mostrar_graf": "📊 Show historical chart"
    }
}
t = idiomas[idioma_actual]

SYMB = {"EUR": "€", "USD": "$", "BRL": "R$"}

dicas = {
    "BRL": {
        "es": ["Compara tasas entre bancos antes de cambiar reales.", "El real puede depreciarse en años electorales."],
        "pt": ["Compare taxas entre bancos antes de trocar reais.", "O real pode se desvalorizar em anos eleitorais."],
        "en": ["Compare bank rates before converting BRL.", "BRL may weaken in election years."]
    },
    "USD": {
        "es": ["El dólar es aceptado en muchos países.", "Las tasas de la Fed pesan en el valor global."],
        "pt": ["O dólar é aceito em muitos países.", "As taxas da Fed afetam o valor global."],
        "en": ["Widely accepted worldwide.", "Fed rates move global value."]
    },
    "EUR": {
        "es": ["Estable pero sensible al BCE.", "Segunda moneda en reservas."],
        "pt": ["Estável, porém sensível ao BCE.", "Segunda moeda mais usada em reservas."],
        "en": ["Stable, sensitive to ECB.", "Second most used in reserves."]
    }
}

@st.cache_data
def carregar_curiosidades(archivo: str):
    p = Path(archivo)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]

@st.cache_data
def get_rates_latest(amount, origem, destino):
    url = f"https://api.frankfurter.app/latest?amount={amount}&from={origem}&to={destino}"
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        raise RuntimeError("API error")
    return r.json()

@st.cache_data
def get_series(inicio: date, fim: date, origem: str, destino: str):
    url = f"https://api.frankfurter.app/{inicio}..{fim}?from={origem}&to={destino}"
    r = requests.get(url, timeout=20)
    if r.status_code != 200:
        raise RuntimeError("API error")
    data = r.json()
    rates = data.get("rates", {})
    fechas = sorted(rates.keys())
    valores = [rates[d][destino] for d in fechas]
    fechas_dt = [datetime.strptime(d, "%Y-%m-%d") for d in fechas]
    return fechas_dt, valores

if "hist" not in st.session_state:
    st.session_state.hist = []

st.title(t["titulo"])
st.caption(t["descripcion"])
st.divider()

monedas = ["EUR", "USD", "BRL"]

col1, col2 = st.columns(2)
with col1:
    cantidad = st.number_input(t["valor"], min_value=0.0, value=5.0, step=1.0, format="%.2f")
    origem = st.selectbox(t["de"], monedas, index=0)
with col2:
    destino = st.selectbox(t["para"], monedas, index=2)

if st.button(t["convertir"]):
    try:
        if origem == destino:
            resultado = cantidad
        else:
            data = get_rates_latest(cantidad, origem, destino)
            resultado = float(data["rates"][destino])
        sym_o, sym_d = SYMB.get(origem, ""), SYMB.get(destino, "")
        st.metric(label=t["resultado"], value=f"{sym_d} {resultado:,.2f} {destino}", delta=f"{sym_o} {cantidad:,.2f} {origem}")

        archivo = {"BRL": "curiosidades_br.txt", "EUR": "curiosidades_es.txt", "USD": "curiosities_us.txt"}.get(destino, "")
        linhas = carregar_curiosidades(archivo)
        curio = random.choice(linhas) if linhas else "Curiosidade indisponível."
        st.info(f"🎯 {curio}")

        dica_txt = random.choice(dicas.get(destino, {}).get(idioma_actual, [])) if dicas.get(destino, {}) else ""
        if dica_txt:
            st.warning(f"💡 {dica_txt}")

        st.session_state.hist.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {sym_o} {cantidad:,.2f} {origem} → {sym_d} {resultado:,.2f} {destino}")
    except Exception:
        st.error("❌ " + t["error_api"])

if st.session_state.hist:
    st.subheader(t["historial"])
    for item in reversed(st.session_state.hist[-10:]):
        st.write(item)

st.divider()

st.subheader(t["grafico"])
inicio, fim = st.date_input(t["rango"], [date(2024, 1, 1), date(2024, 12, 31)])

if inicio > fim:
    st.error("⛔ Intervalo inválido: a data inicial não pode ser maior que a final.")
else:
    if st.button(t["mostrar_graf"]):
        try:
            fechas_dt, valores = get_series(inicio, fim, origem, destino)
            if not fechas_dt:
                st.warning("Sem dados para o período escolhido.")
            else:
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(fechas_dt, valores, marker="o")
                ax.set_title(f"{origem} → {destino}")
                ax.set_xlabel("Data" if idioma_actual == "pt" else "Fecha" if idioma_actual == "es" else "Date")
                ax.set_ylabel("Taxa de câmbio" if idioma_actual == "pt" else "Tasa de cambio" if idioma_actual == "es" else "Exchange rate")
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
                fig.autofmt_xdate()
                st.pyplot(fig)
        except Exception:
            st.error("❌ " + t["error_grafico"])

st.caption(t["fuente"])







