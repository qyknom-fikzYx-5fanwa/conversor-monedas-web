import streamlit as st
import requests
from datetime import datetime, date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random

# 🌐 Selector de idioma manual
idioma_actual = st.selectbox("🌍 Elige el idioma", ["es", "pt", "en"], index=0)

# 🗣️ Diccionario de textos por idioma
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
        "fuente": "📊 Datos del Banco Central Europeo. Actualizados diariamente a las 16:00 CET.",
        "error_api": "❌ No se pudo conectar con la API.",
        "error_grafico": "❌ No se pudo generar el gráfico."
    },
    "pt": {
        "titulo": "Conversor de Moedas Inteligente",
        "descripcion": "Conectado ao Banco Central Europeu • Atualizado diariamente às 16:00 CET",
        "valor": "Digite o valor",
        "de": "Moeda de origem",
        "para": "Moeda de destino",
        "convertir": "🔄 Converter",
        "resultado": "Resultado",
        "grafico": "📈 Mostrar gráfico histórico",
        "rango": "Escolha o intervalo de datas",
        "historial": "🕒 Histórico de conversões",
        "fuente": "📊 Dados do Banco Central Europeu. Atualizados diariamente às 16:00 CET.",
        "error_api": "❌ Erro ao conectar com a API.",
        "error_grafico": "❌ Não foi possível gerar o gráfico."
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
        "historial": "🕒 Conversion History",
        "fuente": "📊 Data from the European Central Bank. Updated daily at 16:00 CET.",
        "error_api": "❌ Could not connect to the API.",
        "error_grafico": "❌ Could not generate the chart."
    }
}

texto = idiomas[idioma_actual]
monedas = ["EUR", "USD", "BRL"]
historial = []

# 📌 Consejos financieros por moneda e idioma
dicas = {
    "BRL": {
        "es": ["💡 Compara tasas entre bancos antes de cambiar reales.", "📊 El real puede depreciarse en años electorales."],
        "pt": ["💡 Compare taxas entre bancos antes de trocar reais.", "📊 O real pode se desvalorizar em anos eleitorais."],
        "en": ["💡 Compare exchange rates before converting BRL.", "📊 BRL may weaken during election years."]
    },
    "USD": {
        "es": ["💵 El dólar es aceptado en muchos países.", "📈 Las tasas de interés en EE.UU. afectan el valor global."],
        "pt": ["💵 O dólar é aceito em muitos países.", "📈 Taxas de juros nos EUA afetam o valor global."],
        "en": ["💵 The dollar is accepted worldwide.", "📈 U.S. interest rates influence global value."]
    },
    "EUR": {
        "es": ["💶 El euro es estable, pero sensible al BCE.", "🌍 Es la segunda moneda más usada en reservas."],
        "pt": ["💶 O euro é estável, mas sensível às decisões do BCE.", "🌍 É a segunda moeda mais usada em reservas."],
        "en": ["💶 The euro is stable but sensitive to ECB decisions.", "🌍 It's the second most used currency globally."]
    }
}

# 📚 Curiosidades por país
def mostrar_curiosidad(moneda):
    archivo = {
        "BRL": "curiosidades_br.txt",
        "EUR": "curiosidades_es.txt",
        "USD": "curiosities_us.txt"
    }.get(moneda, "")
    try:
        with open(archivo, "r", encoding="utf-8") as f:
            frases = f.readlines()
            return random.choice(frases).strip()
    except:
        return "⚠️ Curiosidad no disponible."

def mostrar_dica(moneda):
    if moneda in dicas and idioma_actual in dicas[moneda]:
        return random.choice(dicas[moneda][idioma_actual])
    return ""

# 🖼️ Interfaz principal
st.set_page_config(page_title=texto["titulo"], layout="centered")
st.title(texto["titulo"])
st.caption(texto["descripcion"])
st.divider()

# 💱 Conversión
col1, col2 = st.columns(2)
with col1:
    cantidad = st.number_input(texto["valor"], min_value=0.0, value=1.0)
    origen = st.selectbox(texto["de"], monedas, index=0)
with col2:
    destino = st.selectbox(texto["para"], monedas, index=2)

if st.button(texto["convertir"]):
    try:
        if origen == destino:
            resultado = cantidad
        else:
            url = f"https://api.frankfurter.app/latest?amount={cantidad}&from={origen}&to={destino}"
            data = requests.get(url).json()
            resultado = data["rates"][destino]
        st.metric(label=texto["resultado"], value=f"{resultado:.2f} {destino}", delta=f"{cantidad} {origen}")
        st.info(f"📌 {mostrar_curiosidad(destino)}")
        st.warning(f"{mostrar_dica(destino)}")
        historial.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {cantidad} {origen} → {resultado:.2f} {destino}")
    except:
        st.error(texto["error_api"])

# 🕒 Historial
if historial:
    st.subheader(texto["historial"])
    for item in reversed(historial[-10:]):
        st.write(item)

st.divider()

# 📈 Gráfico histórico
st.subheader(texto["grafico"])
inicio, fin = st.date_input(texto["rango"], [date(2024, 1, 1), date(2024, 12, 31)])

if st.button("📊 " + texto["grafico"]):
    try:
        url = f"https://api.frankfurter.app/{inicio}..{fin}?from={origen}&to={destino}"
        data = requests.get(url).json()
        fechas = list(data["rates"].keys())
        valores = [data["rates"][f][destino] for f in fechas]
        fechas_dt = [datetime.strptime(f, "%Y-%m-%d") for f in fechas]

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(fechas_dt, valores, marker="o", color="royalblue")
        ax.set_title(f"{origen} → {destino}")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Tasa de cambio")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        fig.autofmt_xdate()
        st.pyplot(fig)
    except:
        st.error(texto["error_grafico"])

st.caption(texto["fuente"])






