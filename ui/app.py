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

# Primul apel Streamlit din script (altfel: missing ScriptRunContext)
st.set_page_config(
    page_title="CareSurge AI | Dashboard",
    page_icon="",
    layout="wide"
)

from core.ai_engine import llm_process, what_if_process

# Inițializăm starea analizei (după set_page_config)
if "analiza_vizibila" not in st.session_state:
    st.session_state.analiza_vizibila = False
if "what_if_response" not in st.session_state:
    st.session_state.what_if_response = None
if "response" not in st.session_state:
    st.session_state.response = None

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
    st.header("Configurare Raport")
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
    st.session_state.response = llm_process(lat_curenta, lon_curenta, data_selectata)
    st.session_state.analiza_vizibila = True
    st.session_state.what_if_response = None

# --- HEADER APLICAȚIE ---
if spital_selectat:
    st.title(f"{spital_selectat}")
    st.markdown(f"**Locație:** {oras_afisare} | **Data Raportului:** {data_selectata.strftime('%d %B %Y')}")
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

    tab_simulator, tab_what_if = st.tabs(["Raport de Risc", "What-If Simulator"])
    with tab_simulator:
        st.markdown("#### Raport de Risc")
        st.info(st.session_state.response)

    with tab_what_if:
        st.markdown("#### Simulator What-If")
        st.markdown("Adresează orice întrebare sau scenariu ipotetic, iar AI-ul va răspunde pe baza predicțiilor modelului Prophet.")

        prompt_what_if = st.text_area(
            "Introduceți scenariul sau întrebarea:",
            placeholder="Ex: Ce se întâmplă dacă mâine ninge abundent? Câți pacienți suplimentari ar putea veni?",
            height=120,
            key="prompt_what_if_input"
        )
        what_if_btn = st.button("Analizează Scenariul", type="primary", disabled=not prompt_what_if.strip(), key="what_if_btn")

        if what_if_btn and prompt_what_if.strip():
            with st.spinner("Se analizează scenariul cu modelul Prophet..."):
                st.session_state.what_if_response = what_if_process(lat_curenta, lon_curenta, data_selectata, prompt_what_if.strip())

        if st.session_state.what_if_response:
            st.markdown("---")
            st.markdown("**Răspuns AI bazat pe modelul Prophet:**")
            st.info(st.session_state.what_if_response)