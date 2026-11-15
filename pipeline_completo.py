import os
import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="NASA FIRMS | Harmonized Thermal Anomaly Archive (2012–2025)",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- ESTILO INSTITUCIONAL NASA EARTHDATA / FIRMS ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #0B0D10;
        color: #E6EDF3;
    }

    .stApp {
        background-color: #0B0D10;
    }

    /* Barra superior estilo NASA Earthdata */
    .nasa-header {
        background-color: #10141D;
        border-bottom: 2px solid #0B3D91;
        border-top: 1px solid #232A37;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .nasa-badge {
        background-color: #0B3D91;
        color: #FFFFFF;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1.5px;
        padding: 4px 10px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 6px;
    }
    .nasa-title {
        font-size: 22px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.3px;
        margin: 0;
    }
    .nasa-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        color: #8B949E;
        margin-top: 4px;
    }

    /* Tarjetas de telemetría (bordes rectos, estilo consola) */
    div[data-testid="metric-container"] {
        background-color: #12161F;
        border: 1px solid #252C3A;
        border-left: 3px solid #FC3D21;
        border-radius: 0px;
        padding: 14px 18px;
    }
    div[data-testid="metric-container"] label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #8B949E;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 24px;
        font-weight: 600;
        color: #F0F6FC;
    }

    /* Sidebar estilo panel de control FIRMS */
    section[data-testid="stSidebar"] {
        background-color: #0E121A;
        border-right: 1px solid #232A37;
    }

    /* Pestañas sobrias sin redondeo excesivo */
    button[data-baseweb="tab"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        border-radius: 0px !important;
    }

    /* Botones institucionales */
    .stButton > button, .stDownloadButton > button {
        background-color: #0B3D91;
        color: #FFFFFF;
        border: 1px solid #1C67E3;
        border-radius: 0px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        padding: 8px 16px;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background-color: #1552B8;
        border-color: #4D8DF7;
        color: #FFFFFF;
    }

    .section-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #58A6FF;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        border-bottom: 1px solid #232A37;
        padding-bottom: 6px;
        margin-top: 12px;
        margin-bottom: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CARPETA_BASE = r"C:\Users\cuito\OneDrive\Escritorio\burros"
RUTA_DB = os.path.join(CARPETA_BASE, "incendios_db_general_2012_2025.parquet")
RUTA_MODELO = os.path.join(CARPETA_BASE, "modelo_incendios_lgbm.pkl")


@st.cache_data
def cargar_datos():
    return pd.read_parquet(RUTA_DB)