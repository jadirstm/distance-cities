
import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# =========================
#  CONFIGURAÇÕES DO APP
# =========================
st.set_page_config(
    page_title="Distância até a Capital",
    page_icon="📍",
    layout="centered"
)

# TÍTULO E DESCRIÇÃO
st.title("📍 Calculadora de Distância até a Capital")
st.markdown("""
Este aplicativo calcula a **distância de cada cidade até a capital do estado**  
e classifica em faixas de distância:
- Até 50 km  
- Entre 51 e 100 km  
- Mais de 100 km  

Envie sua planilha Excel com as colunas **Cidade** e **Estado** (UF).
""")

# Upload do arquivo
arquivo = st.file_uploader("📂 Envie sua planilha (.xlsx)", type=["xlsx"])

# Dicionário de capitais
capitais = {
    "AC": "Rio Branco", "AL": "Maceió", "AP": "Macapá", "AM": "Manaus",
    "BA": "Salvador", "CE": "Fortaleza", "DF": "Brasília", "ES": "Vitória",
    "GO": "Goiânia", "MA": "São Luís", "MT": "Cuiabá", "MS": "Campo Grande",
    "MG": "Belo Horizonte", "PA": "Belém", "PB": "João Pessoa", "PR": "Curitiba",
    "PE": "Recife", "PI": "Teresina", "RJ": "Rio de Janeiro", "RN": "Natal",
    "RS": "Porto Alegre", "RO": "Porto Velho", "RR": "Boa Vista", "SC": "Florianópolis",
    "SP": "São Paulo", "SE": "Aracaju", "TO": "Palmas"
}

# Função principal
def calcular_distancias(df):
    geolocator = Nominatim(user_agent="distancia_cidades_app")
    distancias, faixas = [], []

    for _, row in df.iterrows():
        cidade = str(row['Cidade']).strip()
        estado = str(row['Estado']).strip().upper()
        capital = capitais.get(estado, None)

        if not capital:
            distancias.append(None)
            faixas.append("Estado inválido")
            continue

        try:
            local_cidade = geolocator.geocode(f"{cidade}, {estado}, Brasil")
            local_capital = geolocator.geocode(f"{capital}, {estado}, Brasil")

            if local_cidade and local_capital:
                dist = geodesic(
                    (local_cidade.latitude, local_cidade.longitude),
                    (local_capital.latitude, local_capital.longitude)
                ).km

                if dist <= 50:
                    faixa = "Até 50 km"
                elif dist <= 100:
                    faixa = "Entre 51 e 100 km"
                else:
                    faixa = "Mais de 100 km"

                distancias.append(round(dist, 1))
                faixas.append(faixa)
            else:
                distancias.append(None)
                faixas.append("Não encontrado")

        except Exception:
            distancias.append(None)
            faixas.append("Erro")
        time.sleep(1)

    df["Distância (km)"] = distancias
    df["Faixa de Distância"] = faixas
    return df

# Quando o arquivo for enviado
if arquivo is not None:
    df = pd.read_excel(arquivo)
    st.write("📄 **Prévia da planilha enviada:**")
    st.dataframe(df.head())

    if st.button("▶️ Calcular Distâncias"):
        with st.spinner("Calculando... Aguarde um momento."):
            resultado = calcular_distancias(df)

        st.success("✅ Cálculo concluído!")
        st.dataframe(resultado.head())

        # Download
        output = pd.ExcelWriter("resultado.xlsx", engine="openpyxl")
        resultado.to_excel(output, index=False)
        output.close()

        with open("resultado.xlsx", "rb") as f:
            st.download_button(
                label="💾 Baixar resultado",
                data=f,
                file_name="resultado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
