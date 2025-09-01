import streamlit as st
import requests
from datetime import datetime, date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random
import locale

# 🌐 Detectar idioma del sistema
idioma_sistema = locale.getlocale()[0] or "en"
if idioma_sistema.startswith("pt"):
    idioma_actual = "pt"
elif idioma_sistema.startswith("es"):
    idioma_actual = "es"
else:
    idioma_actual = "en"

# 🗣️ Diccionario de idiomas
idiomas = {
    "pt": {
        "titulo": "💱 Conversor de Moedas Inteligente",
        "descricao": "Conectado ao Banco Central Europeu • Atualizado diariamente às 16:00 CET",
        "valor": "Digite o valor",
        "de": "Moeda de origem",
        "para": "Moeda de destino",
        "converter": "🔄 Converter",
        "resultado": "Resultado",
        "grafico": "📈 Mostrar gráfico histórico",
        "datas": "Escolha o intervalo de datas",
        "fonte": "📊 Dados do Banco Central Europeu. Atualizados diariamente às 16:00 CET."
    },
    "es": {
        "titulo": "💱 Conversor de Monedas Inteligente",
        "descricao": "Conectado al Banco Central Europeo • Actualizado diariamente a las 16:00 CET",
        "valor": "Introduce el valor",
        "de": "Moneda de origen",
        "para": "Moneda de destino",
        "converter": "🔄 Convertir",
        "resultado": "Resultado",
        "grafico": "📈 Mostrar gráfico histórico",
        "datas": "Selecciona el rango de fechas",
        "fonte": "📊 Datos del Banco Central Europeo. Actualizados diariamente a las 16:00 CET."
    },
    "en": {
        "titulo": "💱 Smart Currency Converter",
        "descricao": "Connected to the European Central Bank • Updated daily at 16:00 CET",
        "valor": "Enter amount",
        "de": "From currency",
        "para": "To currency",
        "converter": "🔄 Convert",
        "resultado": "Result",
        "grafico": "📈 Show historical chart",
        "datas": "Select date range",
        "fonte": "📊 Data from the European Central Bank. Updated daily at 16:00 CET."
    }
}

texto = idiomas[idioma_actual]
monedas = ["EUR", "USD", "BRL"]
historial = []

# 💡 Consejos financieros
dicas = {
    "BRL": {
        "pt": ["💡 Compare taxas entre bancos antes de trocar reais.", "📊 O real pode se desvalorizar em anos eleitorais."],
        "es": ["💡 Compara tasas entre bancos antes de cambiar reales.", "📊 El real puede depreciarse en años electorales."],
        "en": ["💡 Compare exchange rates before converting BRL.", "📊 BRL may weaken during election years."]
    },
    "USD": {
        "pt": ["💵 O dólar é aceito em muitos países.", "📈 Taxas de juros nos EUA afetam o valor global."],
        "es": ["💵 El dólar es aceptado en muchos países.", "📈 Las tasas de interés en EE.UU. afectan el valor global."],
        "en": ["💵 The dollar is accepted worldwide.", "📈 U.S. interest rates influence global value."]
    },
    "EUR": {
        "pt": ["💶 O euro é estável, mas sensível às decisões do BCE.", "🌍 É a segunda moeda mais usada em reservas."],
        "es": ["💶 El euro es estable, pero sensible al BCE.", "🌍 Es la segunda moneda más usada en reservas."],
        "en": ["💶 The euro is stable but sensitive to ECB decisions.", "🌍 It's the second most used currency globally."]
    }
}

def mostrar_curiosidade(moeda):
    try:
        with open("curiosidades_moedas.txt", "r", encoding="utf-8") as f:
            todas = f.readlines()
            filtradas = [linha.split(": ", 1)[1].strip() for linha in todas if linha.startswith(moeda + ":")]
            if filtradas:
                return random.choice(filtradas)
    except:
        return "⚠️ Curiosidade não disponível."
    return ""

def mostrar_dica(moeda):
    if moeda in dicas and idioma_actual in dicas[moeda]:
        return random.choice(dicas[moeda][idioma_actual])
    return ""

# 🖼️ Interface Streamlit
st.set_page_config(page_title=texto["titulo"], layout="centered")
st.title(texto["titulo"])
st.caption(texto["descricao"])
st.divider()

# 💱 Conversão
col1, col2 = st.columns(2)
with col1:
    cantidad = st.number_input(texto["valor"], min_value=0.0, value=1.0)
    origen = st.selectbox(texto["de"], monedas, index=0)
with col2:
    destino = st.selectbox(texto["para"], monedas, index=2)

if st.button(texto["converter"]):
    try:
        if origen == destino:
            resultado = cantidad
        else:
            url = f"https://api.frankfurter.app/latest?amount={cantidad}&from={origen}&to={destino}"
            data = requests.get(url).json()
            resultado = data["rates"][destino]
        st.metric(label=texto["resultado"], value=f"{resultado:.2f} {destino}", delta=f"{cantidad} {origen}")
        st.info(f"📌 {mostrar_curiosidade(destino)}")
        st.warning(f"{mostrar_dica(destino)}")
        historial.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {cantidad} {origen} → {resultado:.2f} {destino}")
    except:
        st.error("❌ Erro ao conectar com a API.")

# 📜 Historial
if historial:
    st.subheader("🕒 Histórico")
    for item in reversed(historial[-10:]):
        st.write(item)

st.divider()

# 📈 Gráfico histórico
st.subheader(texto["grafico"])
inicio, fim = st.date_input(texto["datas"], [date(2024, 1, 1), date(2024, 12, 31)])

if st.button("📊 Gerar gráfico"):
    try:
        url = f"https://api.frankfurter.app/{inicio}..{fim}?from={origen}&to={destino}"
        data = requests.get(url).json()
        fechas = list(data["rates"].keys())
        valores = [data["rates"][f][destino] for f in fechas]
        fechas_dt = [datetime.strptime(f, "%Y-%m-%d") for f in fechas]

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(fechas_dt, valores, marker="o", color="royalblue")
        ax.set_title(f"{origen} → {destino}")
        ax.set_xlabel("Data")
        ax.set_ylabel("Taxa de câmbio")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        fig.autofmt_xdate()
        st.pyplot(fig)
    except:
        st.error("❌ Não foi possível gerar o gráfico.")

st.caption(texto["fonte"])



