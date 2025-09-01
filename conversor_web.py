conversor_web
import streamlit as st
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random
import locale

# Detectar idioma del sistema
idioma_sistema = locale.getlocale()[0] or "en"
if idioma_sistema.startswith("pt"):
    idioma_actual = "pt"
elif idioma_sistema.startswith("es"):
    idioma_actual = "es"
else:
    idioma_actual = "en"

# Diccionario de idiomas
idiomas = {
    "pt": {
        "titulo": "Conversor de Moedas",
        "cantidad": "Quantidade",
        "origen": "De",
        "destino": "Para",
        "convertir": "Converter",
        "resultado": "Resultado",
        "historial": "Histórico de conversões",
        "grafico": "Gráfico histórico",
        "fecha_inicio": "Data inicial",
        "fecha_fin": "Data final",
        "fonte": "📊 Dados do Banco Central Europeu. Atualizados diariamente às 16:00 CET."
    },
    "es": {
        "titulo": "Conversor de Monedas",
        "cantidad": "Cantidad",
        "origen": "De",
        "destino": "A",
        "convertir": "Convertir",
        "resultado": "Resultado",
        "historial": "Historial de conversiones",
        "grafico": "Gráfico histórico",
        "fecha_inicio": "Fecha inicio",
        "fecha_fin": "Fecha fin",
        "fonte": "📊 Datos del Banco Central Europeo. Actualizados diariamente a las 16:00 CET."
    },
    "en": {
        "titulo": "Currency Converter",
        "cantidad": "Amount",
        "origen": "From",
        "destino": "To",
        "convertir": "Convert",
        "resultado": "Result",
        "historial": "Conversion History",
        "grafico": "Historical Chart",
        "fecha_inicio": "Start date",
        "fecha_fin": "End date",
        "fonte": "📊 Data from the European Central Bank. Updated daily at 16:00 CET."
    }
}

texto = idiomas[idioma_actual]
monedas = ["USD", "EUR", "BRL"]
historial = []

# Consejos financieros
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

# Interfaz Streamlit
st.set_page_config(page_title=texto["titulo"], layout="centered")
st.title(texto["titulo"])

col1, col2 = st.columns(2)
with col1:
    cantidad = st.number_input(texto["cantidad"], min_value=0.0, value=1.0)
    origen = st.selectbox(texto["origen"], monedas, index=0)
with col2:
    destino = st.selectbox(texto["destino"], monedas, index=2)

if st.button(texto["convertir"]):
    try:
        if origen == destino:
            resultado = cantidad
        else:
            url = f"https://api.frankfurter.app/latest?amount={cantidad}&from={origen}&to={destino}"
            data = requests.get(url).json()
            resultado = data["rates"][destino]
        texto_resultado = f"{cantidad} {origen} = {resultado:.2f} {destino}"
        st.success(f"{texto['resultado']}: {texto_resultado}")
        historial.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | {texto_resultado}")
        st.markdown(f"**💬 {mostrar_curiosidade(destino)}**")
        st.markdown(f"**📌 {mostrar_dica(destino)}**")
    except:
        st.error(texto["error_conexion"])

if historial:
    st.subheader(texto["historial"])
    for item in reversed(historial[-10:]):
        st.write(item)

st.subheader(texto["grafico"])
col3, col4 = st.columns(2)
with col3:
    inicio = st.text_input(texto["fecha_inicio"], value="2024-01-01")
with col4:
    fin = st.text_input(texto["fecha_fin"], value="2024-12-31")

if st.button("📈 Mostrar gráfico"):
    try:
        url = f"https://api.frankfurter.app/{inicio}..{fin}?from={origen}&to={destino}"
        data = requests.get(url).json()
        fechas = list(data["rates"].keys())
        valores = [data["rates"][f][destino] for f in fechas]
        fechas_dt = [datetime.strptime(f, "%Y-%m-%d") for f in fechas]

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(fechas_dt, valores, marker="o")
        ax.set_title(f"{origen} → {destino}")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Tasa de cambio")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        fig.autofmt_xdate()
        st.pyplot(fig)
    except:
        st.error(texto["error_conexion"])

st.caption(texto["fonte"])
