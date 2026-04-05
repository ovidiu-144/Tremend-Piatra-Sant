import os
import sys

base_path = os.path.dirname(os.path.dirname(__file__))

if base_path not in sys.path:
    sys.path.append(base_path)

import pandas as pd
import numpy as np
import time
import unicodedata
import streamlit as st
from datetime import date, timedelta
from core.ai_engine import llm_process

# Inițializăm memoria chat-ului și starea analizei
if "istoric_chat" not in st.session_state:
    st.session_state.istoric_chat = []
if "analiza_vizibila" not in st.session_state:
    st.session_state.analiza_vizibila = False

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(
    page_title="CareSurge AI | Dashboard",
    page_icon="🏥",
    layout="wide"
)

# --- FUNCȚIE PENTRU ELIMINAREA DIACRITICELOR ---
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    text = unicodedata.normalize('NFKD', text)
    text_fara_diacritice = "".join([c for c in text if not unicodedata.combining(c)])
    return text_fara_diacritice.lower().strip()

# --- ÎNCĂRCARE DATE ---
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, '..', 'data', 'spitale.csv')
    
    if not os.path.exists(csv_path):
        csv_path = 'spitale.csv'
        
    df = pd.read_csv(csv_path)
    df['oras'] = df['oras'].astype(str).str.strip()
    df['nume'] = df['nume'].astype(str).str.strip()
    
    df['oras_search'] = df['oras'].apply(normalize_text)
    return df

df_spitale = load_data()

# --- STYLE (CSS MINIMAL) ---
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: INPUT DATE ---
with st.sidebar:
    st.header("📍 Configurare Raport")
    st.markdown("Selectați parametrii pentru analiza de risc.")
    st.divider()
    
    def reseteaza_analiza():
        st.session_state.analiza_vizibila = False
        
    oras_introdus = st.text_input("Oraș:", placeholder="ex: Bucuresti, Cluj", on_change=reseteaza_analiza).strip()
    
    spital_selectat = None
    oras_afisare = ""
    data_selectata = date.today()

    if oras_introdus:
        oras_cautare = normalize_text(oras_introdus)
        df_filtrat = df_spitale[df_spitale['oras_search'] == oras_cautare]
        
        if not df_filtrat.empty:
            lista_spitale = sorted(df_filtrat['nume'].unique().tolist())
            spital_selectat = st.selectbox("Unitate Medicală:", lista_spitale, on_change=reseteaza_analiza)
            
            # Păstrăm numele orașului pentru afișare
            oras_afisare = df_filtrat.iloc[0]['oras']
            
            if spital_selectat:
                # --- EXTRAGEREA LATITUDINII ȘI LONGITUDINII ---
                # Filtrăm df_filtrat pentru a găsi rândul exact al spitalului selectat
                date_spital = df_filtrat[df_filtrat['nume'] == spital_selectat].iloc[0]
                
                # Salvăm coordonatele în variabile (verifică dacă în CSV coloanele se numesc 'lat' și 'long')
                lat_curenta = date_spital['lat']
                lon_curenta = date_spital['long']
                
                # Introducere dată
                data_selectata = st.date_input(
                    "Selectează Data Analizei:",
                    value=date.today(),
                    min_value=date.today(),
                    max_value=date.today() + timedelta(days=14),
                    on_change=reseteaza_analiza
                )
        else:
            st.warning(f"Nu am găsit rezultate pentru '{oras_introdus}'.")
    
    st.divider()
    buton_activ = spital_selectat is not None
    predict_btn = st.button("🔍 Generează Raport de Risc", use_container_width=True, disabled=not buton_activ, type="primary")

if predict_btn:
    response = llm_process(lat_curenta, lon_curenta, data_selectata)
    st.session_state.analiza_vizibila = True

# --- HEADER APLICAȚIE ---
if spital_selectat:
    st.title(f"🏥 {spital_selectat}")
    st.markdown(f"**📍 Locație:** {oras_afisare} | **📅 Data Raportului:** {data_selectata.strftime('%d %B %Y')}")
    st.divider()
else:
    st.title("👋 Bine ai venit în CareSurge AI")
    st.markdown("""
    **Platforma de Triaj Predictiv On-Demand**
    
    Acest sistem analizează contextul geospațial pentru a identifica riscurile de suprasolicitare medicală.
    
    👉 **Instrucțiuni:**
    Selectați orașul, spitalul și data din meniul lateral pentru a genera raportul text-based.
    """)

# --- LOGICĂ AFISARE REZULTATE ---
if st.session_state.analiza_vizibila:
    if predict_btn:
        with st.spinner('Se procesează datele de risc...'):
            time.sleep(1.2) 
    risc = 82 if normalize_text(oras_introdus) in ["constanta", "brasov", "bucuresti"] else 38

    tab_simulator, = st.tabs(["⚠️ Raport de Risc"])
    with tab_simulator:
        st.markdown("#### Simulator de Criză (What-If)")
        st.info(response)

        
        for mesaj in st.session_state.istoric_chat:
            with st.chat_message(mesaj["rol"]):
                st.markdown(mesaj["text"])
                
        scenariu = st.chat_input("Ex: Ce facem dacă avem o pană de curent generală?")
        if scenariu:
            st.session_state.istoric_chat.append({"rol": "user", "text": scenariu})
            st.session_state.istoric_chat.append({"rol": "assistant", "text": f"**Analiză pentru {spital_selectat}:** Scenariul de tip '{scenariu}' ar ridica riscul UPU la 95%. Recomandăm activarea generatoarelor și a protocolului de triaj manual."})
            st.rerun()