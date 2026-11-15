import os
import json
import pandas as pd

carpeta_base = r"C:\Users\cuito\OneDrive\Escritorio\burros"
ruta_parquet = os.path.join(carpeta_base, "incendios_armonizados_2012_2025.parquet")
carpeta_salida = os.path.join(carpeta_base, "web_data")
os.makedirs(carpeta_salida, exist_ok=True)

print("Cargando dataset armonizado...")
df = pd.read_parquet(ruta_parquet)

# Crear identificador espacial (~1.1 km) para evitar doble conteo MODIS + VIIRS en el mismo evento
df["lat_grid"] = df["latitude"].round(2)
df["lon_grid"] = df["longitude"].round(2)

# 1. Comparativa anual (2012 - 2025)
anual = (
    df.groupby(["anio", "sensor"])
    .agg(
        detecciones=("temp_brillo", "count"),
        frp_total_mw=("frp", "sum"),
        temp_brillo_prom=("temp_brillo", "mean"),
    )
    .reset_index()
)

# Eventos únicos armonizados por año (deduplicando píxeles cercanos en el mismo día)
eventos_anuales = (
    df.drop_duplicates(subset=["acq_date", "lat_grid", "lon_grid"])
    .groupby("anio")
    .agg(
        eventos_unicos=("temp_brillo", "count"),
        frp_total_armonizado_mw=("frp", "sum"),
    )
    .reset_index()
)

# 2. Periodos pico (estacionalidad mensual histórica 2012 - 2025)
nombres_meses = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

mensual = (
    df.drop_duplicates(subset=["acq_date", "lat_grid", "lon_grid"])
    .groupby("mes")
    .agg(
        eventos_unicos=("temp_brillo", "count"),
        frp_total_mw=("frp", "sum"),
        temp_brillo_max=("temp_brillo", "max"),
    )
    .reset_index()
)
mensual["mes_nombre"] = mensual["mes"].map(nombres_meses)

# Identificar los 3 meses pico históricos
top_meses = mensual.sort_values(by="eventos_unicos", ascending=False).head(3)

# 3. Exportar JSON ligero para las gráficas del Dashboard Web
resumen_dashboard = {
    "total_registros_crudos": int(len(df)),
    "total_eventos_unicos": int(eventos_anuales["eventos_unicos"].sum()),
    "rango_anios": [int(df["anio"].min()), int(df["anio"].max())],
    "meses_pico": top_meses[["mes", "mes_nombre", "eventos_unicos", "frp_total_mw"]].to_dict(orient="records"),
    "comparativa_anual_sensores": anual.round(2).to_dict(orient="records"),
    "comparativa_anual_armonizada": eventos_anuales.round(2).to_dict(orient="records"),
    "estacionalidad_mensual": mensual.round(2).to_dict(orient="records"),
}

ruta_json = os.path.join(carpeta_salida, "metricas_dashboard.json")
with open(ruta_json, "w", encoding="utf-8") as f:
    json.dump(resumen_dashboard, f, ensure_ascii=False, indent=2)

# 4. Exportar CSV limpio para descarga directa desde el Dashboard
# (Filtramos confianza nominal/high para calidad científica y seleccionamos columnas clave)
cols_csv = [
    "acq_date", "acq_time", "anio", "mes", "latitude", "longitude",
    "sensor", "temp_brillo", "frp", "confianza_armonizada", "daynight"
]
df_csv = df[df["confianza_armonizada"].isin(["nominal", "high"])][cols_csv]
ruta_csv = os.path.join(carpeta_salida, "incendios_mexico_armonizado_2012_2025.csv")
df_csv.to_csv(ruta_csv, index=False)

# 5. Muestra ligera (último año 2025) en JSON para renderizar puntos rápidos en el mapa inicial
df_mapa_2025 = (
    df[(df["anio"] == 2025) & (df["confianza_armonizada"] == "high")]
    [["acq_date", "latitude", "longitude", "sensor", "temp_brillo", "frp"]]
    .copy()
)
df_mapa_2025["acq_date"] = df_mapa_2025["acq_date"].dt.strftime("%Y-%m-%d")
ruta_mapa = os.path.join(carpeta_salida, "puntos_mapa_2025.json")
df_mapa_2025.to_json(ruta_mapa, orient="records")

print("\n--- RESUMEN GENERADO ---")
print(f"Total registros armonizados: {len(df):,}")
print(f"Eventos únicos (~1 km/día): {eventos_anuales['eventos_unicos'].sum():,}")
print("Top 3 meses pico históricos:")
for _, row in top_meses.iterrows():
    print(f"  - {row['mes_nombre']}: {row['eventos_unicos']:,} eventos | FRP: {row['frp_total_mw']:,.1f} MW")
print(f"\nArchivos listos en: {carpeta_salida}")