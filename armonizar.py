import glob
import os
import pandas as pd

# 1. Buscar todos los archivos parquet de MODIS y VIIRS en la carpeta actual
archivos_modis = sorted(glob.glob("modis_bb_*.parquet"))
archivos_viirs = sorted(glob.glob("viirs_snpp_bb_*.parquet"))

print(
    f"Encontrados: {len(archivos_modis)} archivos MODIS y"
    f" {len(archivos_viirs)} archivos VIIRS."
)


def estandarizar_confianza_modis(valor):
    """Convierte el porcentaje (0-100) de MODIS a las categorías de VIIRS (low, nominal, high)."""
    try:
        v = float(valor)
        if v < 30:
            return "low"
        elif v < 80:
            return "nominal"
        else:
            return "high"
    except (ValueError, TypeError):
        return "nominal"


def procesar_modis(lista_archivos):
    dfs = []
    for archivo in lista_archivos:
        df = pd.read_parquet(archivo)

        # Renombrar columnas para igualar el esquema estándar
        df = df.rename(
            columns={
                "brightness": "temp_brillo",
                "bright_t31": "temp_brillo_secundaria",
            }
        )

        # Armonizar confianza numérica a categórica
        if "confidence" in df.columns:
            df["confianza_armonizada"] = df["confidence"].apply(
                estandarizar_confianza_modis
            )

        df["sensor"] = "MODIS"
        df["resolucion_m"] = 1000
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def procesar_viirs(lista_archivos):
    dfs = []
    mapa_confianza = {
        "l": "low",
        "n": "nominal",
        "h": "high",
        "low": "low",
        "nominal": "nominal",
        "high": "high",
    }

    for archivo in lista_archivos:
        df = pd.read_parquet(archivo)

        # Renombrar columnas de temperatura de VIIRS al mismo estándar
        df = df.rename(
            columns={
                "bright_ti4": "temp_brillo",
                "bright_ti5": "temp_brillo_secundaria",
            }
        )

        # Armonizar letras ('l', 'n', 'h') a palabras completas
        if "confidence" in df.columns:
            df["confianza_armonizada"] = (
                df["confidence"]
                .astype(str)
                .str.lower()
                .map(mapa_confianza)
                .fillna("nominal")
            )

        df["sensor"] = "VIIRS"
        df["resolucion_m"] = 375
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


# 2. Procesar ambos conjuntos
df_modis_clean = procesar_modis(archivos_modis)
df_viirs_clean = procesar_viirs(archivos_viirs)

# 3. Definir las columnas finales comunes para tu dashboard y CSV
columnas_comunes = [
    "latitude",
    "longitude",
    "acq_date",
    "acq_time",
    "temp_brillo",
    "temp_brillo_secundaria",
    "frp",  # Fire Radiative Power (MW) - ya es compatible en ambos
    "confianza_armonizada",
    "sensor",
    "resolucion_m",
    "satellite",
    "daynight",
]

# Filtrar solo las columnas que existan en ambos dataframes
cols_finales = [
    c
    for c in columnas_comunes
    if c in df_modis_clean.columns and c in df_viirs_clean.columns
]

# 4. Unir todo en un solo dataset maestro
df_armonizado = pd.concat(
    [df_modis_clean[cols_finales], df_viirs_clean[cols_finales]],
    ignore_index=True,
)

# 5. Limpieza final de fechas y tipos de datos
df_armonizado["acq_date"] = pd.to_datetime(df_armonizado["acq_date"])
df_armonizado["anio"] = df_armonizado["acq_date"].dt.year
df_armonizado["mes"] = df_armonizado["acq_date"].dt.month

# Ordenar cronológicamente
df_armonizado = df_armonizado.sort_values(
    by=["acq_date", "acq_time"]
).reset_index(drop=True)

# 6. Guardar resultado listo para tu mapa web y exportación
df_armonizado.to_parquet("incendios_armonizados_2012_2025.parquet", index=False)
print(
    f"¡Armonización completada! Total de registros: {len(df_armonizado):,}"
)
print(df_armonizado[["acq_date", "sensor", "temp_brillo", "frp", "confianza_armonizada"]].head())