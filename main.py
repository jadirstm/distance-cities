import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
import re
from unidecode import unidecode
import time

st.set_page_config(page_title="Distância até a Capital", layout="centered")
st.title("📍 Calculadora de Distância até a Capital")

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

# Arquivo de cache
CACHE_FILE = "coordenadas_cache.csv"
if os.path.exists(CACHE_FILE):
    cache = pd.read_csv(CACHE_FILE)
else:
    cache = pd.DataFrame(columns=["Cidade","Estado","Latitude","Longitude"])

geolocator = Nominatim(user_agent="distancia_cidades_app")

# Função para padronizar cidade
def padronizar_cidade(cidade):
    cidade = str(cidade)
    cidade = cidade.strip()                   # remove espaços no começo/fim
    cidade = re.sub(r'\s+', ' ', cidade)     # remove múltiplos espaços
    cidade = unidecode(cidade)               # remove acentos
    cidade = cidade.title()                  # transforma em "Capitalized Words"
    return cidade

# Função para obter coordenadas (com cache)
def obter_coordenadas(cidade, estado):
    global cache
    filtro = (cache["Cidade"]==cidade) & (cache["Estado"]==estado)
    if filtro.any():
        lat = cache.loc[filtro, "Latitude"].values[0]
        lon = cache.loc[filtro, "Longitude"].values[0]
        return lat, lon
    # Busca online
    location = geolocator.geocode(f"{cidade}, {estado}, Brasil")
    if location:
        nova_linha = {"Cidade":cidade,"Estado":estado,"Latitude":location.latitude,"Longitude":location.longitude}
        cache = pd.concat([cache,pd.DataFrame([nova_linha])], ignore_index=True)
        cache.to_csv(CACHE_FILE, index=False)
        return location.latitude, location.longitude
    return None, None

# Função para calcular distâncias
def calcular_distancias(df):
    distancias, faixas = [], []
    progresso = st.progress(0)
    total = len(df)
    
    for i, row in df.iterrows():
        cidade = padronizar_cidade(row['Cidade'])
        estado = str(row['Estado']).strip().upper()
        capital = capitais.get(estado,None)
        
        if not capital:
            distancias.append(None)
            faixas.append("Estado inválido")
            progresso.progress(int((i+1)/total*100))
            continue
        
        try:
            lat_cidade, lon_cidade = obter_coordenadas(cidade, estado)
            lat_cap, lon_cap = obter_coordenadas(padronizar_cidade(capital), estado)
            
            if lat_cidade and lat_cap:
                dist = geodesic((lat_cidade, lon_cidade),(lat_cap, lon_cap)).km
                if dist <= 50:
                    faixa = "Até 50 km"
                elif dist <= 100:
                    faixa = "Entre 51 e 100 km"
                else:
                    faixa = "Mais de 100 km"
                distancias.append(round(dist,1))
                faixas.append(faixa)
            else:
                distancias.append(None)
                faixas.append("Cidade não encontrada")
        except:
            distancias.append(None)
            faixas.append("Erro")
        
        progresso.progress(int((i+1)/total*100))
        time.sleep(0.2)

    df["Distância (km)"] = distancias
    df["Faixa de Distância"] = faixas
    return df

# Execução do app
if arquivo is not None:
    df = pd.read_excel(arquivo)
    st.write("📄 **Prévia da planilha enviada:**")
    st.dataframe(df.head())

    if st.button("▶️ Calcular Distâncias"):
        with st.spinner("Calculando..."):
            resultado = calcular_distancias(df)
        st.success("✅ Cálculo concluído!")
        st.dataframe(resultado.head())
        
        # Download
        resultado.to_excel("resultado.xlsx", index=False)
        with open("resultado.xlsx","rb") as f:
            st.download_button(
                label="💾 Baixar resultado",
                data=f,
                file_name="resultado.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
