import pandas as pd
import streamlit as st
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import time
import os

st.set_page_config(page_title="Distância das Capitais", layout="wide")

st.title("📍 Calculadora de Distância até a Capital")

# === Upload do arquivo Excel ===
uploaded_file = st.file_uploader("Envie a planilha Excel com a aba VALIDADA", type=["xlsx"])

# === Função de leitura segura ===
def carregar_planilha_excel(file):
    try:
        df = pd.read_excel(file, sheet_name="VALIDADA")  # lê apenas a aba VALIDADA
        df = df[['Cidade', 'Estado']].dropna()
        df['Cidade'] = df['Cidade'].astype(str).str.strip()
        df['Estado'] = df['Estado'].astype(str).str.strip().str.upper()
        return df
    except Exception as e:
        st.error(f"Erro ao ler planilha: {e}")
        return None

# === Função para calcular coordenadas ===
def obter_coordenadas(cidade, estado, cache):
    chave = f"{cidade}-{estado}"
    if chave in cache:
        return cache[chave]
    
    geolocator = Nominatim(user_agent="distance_app")
    try:
        location = geolocator.geocode(f"{cidade}, {estado}, Brasil", timeout=10)
        if location:
            coordenadas = (location.latitude, location.longitude)
            cache[chave] = coordenadas
            return coordenadas
    except:
        return None
    return None

# === Função para calcular distância até a capital ===
def calcular_distancias(df):
    cache = {}
    resultados = []

    # dicionário com as capitais por UF
    capitais = {
        "SP": "São Paulo", "RJ": "Rio de Janeiro", "MG": "Belo Horizonte", "PR": "Curitiba",
        "SC": "Florianópolis", "RS": "Porto Alegre", "GO": "Goiânia", "DF": "Brasília",
        "BA": "Salvador", "PE": "Recife", "CE": "Fortaleza", "PA": "Belém", "AM": "Manaus",
        "ES": "Vitória", "MT": "Cuiabá", "MS": "Campo Grande", "MA": "São Luís",
        "PB": "João Pessoa", "PI": "Teresina", "RN": "Natal", "RO": "Porto Velho",
        "RR": "Boa Vista", "SE": "Aracaju", "AL": "Maceió", "AP": "Macapá", "TO": "Palmas",
        "AC": "Rio Branco"
    }

    geolocator = Nominatim(user_agent="distance_app")

    for _, row in df.iterrows():
        cidade = row['Cidade']
        estado = row['Estado']
        capital = capitais.get(estado)

        if not capital:
            continue

        origem = obter_coordenadas(cidade, estado, cache)
        destino = obter_coordenadas(capital, estado, cache)

        if origem and destino:
            distancia = geodesic(origem, destino).km
            if distancia <= 50:
                faixa = "Até 50 km"
            elif distancia <= 100:
                faixa = "51 a 100 km"
            else:
                faixa = "Mais de 100 km"
        else:
            distancia = None
            faixa = "Não encontrado"

        resultados.append({
            "Cidade": cidade,
            "Estado": estado,
            "Capital": capital,
            "Distância (km)": round(distancia, 1) if distancia else "Erro",
            "Faixa": faixa
        })
        time.sleep(1)  # respeita limite do geocoding gratuito

    return pd.DataFrame(resultados)

# === Execução ===
if uploaded_file:
    df = carregar_planilha_excel(uploaded_file)
    if df is not None:
        with st.spinner("Calculando distâncias..."):
            resultado = calcular_distancias(df)
            st.success("✅ Cálculo concluído!")
            st.dataframe(resultado)

            # opção para download
            csv = resultado.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Baixar resultado CSV", csv, "distancias_capitais.csv", "text/csv")
