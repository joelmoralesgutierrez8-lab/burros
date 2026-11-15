import os
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="NASA FIRMS Harmonized | Incendios México 2012-2025",
    page_icon="🔥",
    layout="wide",
)

CARPETA_BASE = r"C:\Users\cuito\OneDrive\Escritorio\burros"
RUTA_PARQUET = os.path.join(CARPETA_BASE, "incendios_armonizados_2012_2025.parquet")


@st.cache_data
def cargar_datos():
    df = pd.read_parquet(RUTA_PARQUET)
    df["lat_grid"] = df["latitude"].round(2)
    df["lon_grid"] = df["longitude"].round(2)
    return df


df = cargar_datos()

st.sidebar.header("Filtros de Exploración")

anios_disponibles = sorted(df["anio"].unique())
rango_anios = st.sidebar.select_slider(
    "Rango de años",
    options=anios_disponibles,
    value=(min(anios_disponibles), max(anios_disponibles)),
)

sensores_sel = st.sidebar.multiselect(
    "Sensores satelitales",
    options=df["sensor"].unique().tolist(),
    default=df["sensor"].unique().tolist(),
)

confianza_sel = st.sidebar.multiselect(
    "Nivel de confianza armonizado",
    options=["low", "nominal", "high"],
    default=["nominal", "high"],
)

df_filtrado = df[
    (df["anio"].between(rango_anios[0], rango_anios[1]))
    & (df["sensor"].isin(sensores_sel))
    & (df["confianza_armonizada"].isin(confianza_sel))
]

df_eventos = df_filtrado.drop_duplicates(subset=["acq_date", "lat_grid", "lon_grid"])

st.title("🔥 Monitoreo Histórico de Incendios Armonizado (MODIS + VIIRS)")
st.markdown(
    "Integración multi-sensor (2012–2025) con estandarización de temperatura de brillo, "
    "niveles de confianza y deduplicación espacial (~1.1 km)."
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Detecciones Crudas", f"{len(df_filtrado):,}")
col2.metric("Eventos Únicos (~1 km/día)", f"{len(df_eventos):,}")
col3.metric("FRP Acumulado (MW)", f"{df_filtrado['frp'].sum():,.0f}")

nombres_meses = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}
if not df_eventos.empty:
    mes_pico_num = df_eventos["mes"].value_counts().idxmax()
    col4.metric("Mes Pico Histórico", nombres_meses[mes_pico_num])
else:
    col4.metric("Mes Pico Histórico", "N/A")

st.divider()

graf_col1, graf_col2 = st.columns(2)

with graf_col1:
    st.subheader("Comparativa Anual por Sensor")
    anual_sensor = (
        df_filtrado.groupby(["anio", "sensor"])
        .size()
        .reset_index(name="detecciones")
    )
    fig_anual = px.bar(
        anual_sensor,
        x="anio",
        y="detecciones",
        color="sensor",
        barmode="group",
        labels={"anio": "Año", "detecciones": "Detecciones", "sensor": "Sensor"},
        color_discrete_map={"MODIS": "#FF6B35", "VIIRS": "#004E89"},
    )
    st.plotly_chart(fig_anual, width="stretch")

with graf_col2:
    st.subheader("Periodos Pico (Estacionalidad Mensual)")
    mensual = (
        df_eventos.groupby("mes")
        .agg(eventos=("temp_brillo", "count"), frp_mw=("frp", "sum"))
        .reset_index()
    )
    mensual["mes_nombre"] = mensual["mes"].map(nombres_meses)
    fig_mes = px.area(
        mensual,
        x="mes_nombre",
        y="eventos",
        markers=True,
        labels={"mes_nombre": "Mes", "eventos": "Eventos Únicos"},
        color_discrete_sequence=["#E63946"],
    )
    st.plotly_chart(fig_mes, width="stretch")

st.subheader("Distribución Geográfica de Focos Activos")
anio_mapa = st.selectbox(
    "Selecciona un año específico para visualizar en el mapa (optimizado para navegador):",
    options=sorted(df_filtrado["anio"].unique(), reverse=True),
)

df_mapa = df_filtrado[df_filtrado["anio"] == anio_mapa]
if len(df_mapa) > 15000:
    df_mapa = df_mapa.sample(15000, random_state=42)
    st.caption("Mostrando muestra aleatoria de 15,000 puntos de alta calidad para fluidez del mapa.")

fig_mapa = px.scatter_map(
    df_mapa,
    lat="latitude",
    lon="longitude",
    color="sensor",
    size="frp",
    size_max=12,
    hover_data=["acq_date", "temp_brillo", "frp", "confianza_armonizada"],
    zoom=4.2,
    center={"lat": 23.6, "lon": -102.5},
    map_style="carto-darkmatter",
    color_discrete_map={"MODIS": "#FF9F1C", "VIIRS": "#E71D36"},
)
fig_mapa.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, height=500)
st.plotly_chart(fig_mapa, width="stretch")

st.divider()
st.subheader("Exportación de Datos Armonizados")
st.write(f"Registros listos según los filtros actuales: **{len(df_filtrado):,}**")

csv_bytes = df_filtrado.drop(columns=["lat_grid", "lon_grid"]).to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Descargar dataset filtrado en CSV",
    data=csv_bytes,
    file_name=f"incendios_armonizados_{rango_anios[0]}_{rango_anios[1]}.csv",
    mime="text/csv",
)
