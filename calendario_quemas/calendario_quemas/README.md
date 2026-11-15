# Calendario de quemas — MODIS + VIIRS armonizados (México, 2000–2025)

Proyecto para el reto *MODIS and VIIRS Hot Spots* de NASA Space Apps Challenge 2026.
Tiene dos partes: (1) una serie de hotspots armonizada, donde el sensor de origen deja de importar, y (2) una aplicación web que la usa.

## Contenido

| Carpeta | Qué contiene |
|---|---|
| `app/` | Aplicación web estática (HTML, CSS y JavaScript sin dependencias). Los datos compactos están en `app/data/`. |
| `datos_armonizados/` | Serie armonizada por estado y día, por estado y mes, factores de calibración y tablas de validación. |
| `pipeline/` | Scripts de Python que generan todo lo anterior a partir de los parquet de FIRMS. |
| `figuras/` | Figura estática de dos paneles (factor efectivo por celda y densidad de VIIRS armonizado), para 2012–2020 y 2012–2025. |
| `geo/` | Contornos estatales simplificados (geoBoundaries gbOpen, ADM1 de México). |

## Cómo abrir la aplicación

```bash
cd app
python3 -m http.server 8000
# abrir http://localhost:8000
```

La app carga `data/frag.txt` (3.2 MB) al iniciar y descarga por año, solo cuando se exporta el CSV de hotspots, los archivos de `data/pts/`. Los archivos `.txt` de datos son un gzip codificado en base64: se usa texto porque así los sirve cualquier hosting estático, incluido el de artefactos.

### Capas del mapa

El mapa tiene tres capas y respeta el rango de fechas y la región:

* **Densidad armonizada** (escala de raíz cuadrada o logarítmica): hotspots equivalentes a MODIS por celda de 0.25°.
* **Factor efectivo por celda**: detecciones VIIRS por cada hotspot equivalente a MODIS (`ΣVIIRS / Σarmonizado`) en la era VIIRS del rango; solo celdas con ≥ 20 detecciones VIIRS.
* **Armonizado ÷ MODIS por celda**: control espacial de la armonización (1× = coincide con MODIS observado); solo era VIIRS y celdas con ≥ 20 detecciones MODIS.

La capa visible se descarga como PNG con el botón *PNG del mapa*.

## Cómo regenerar los datos

Requiere Python 3 con `pandas`, `numpy`, `pyarrow`, `geopandas` y `shapely`.

```bash
python3 pipeline/01_load.py     <carpeta_con_parquet> data/all_points.parquet
python3 pipeline/03_footprints.py data/all_points.parquet geo/mex_adm1_full.geojson data/points_state.parquet
python3 pipeline/07_build.py    data/points_state.parquet geo/mex_adm1_full.geojson out
python3 pipeline/08_validation.py data/points_state.parquet out/app_data/validacion.json
```

Después, convierte cada archivo de `out/app_data/` (`frag.bin.gz` y `pts/pts_AAAA.bin.gz`) a base64 y guárdalo en `app/data/` como `frag.txt` y `pts/pts_AAAA.txt`; `meta.json` y `validacion.json` se copian tal cual (`pipeline/10_empaquetar_app.py` hace esto). Los CSV quedan en `out/`.

`mex_adm1_full.geojson` (35 MB) es el límite de detalle completo de geoBoundaries; se descarga de
`https://github.com/wmgeolab/geoBoundaries` (`releaseData/gbOpen/MEX/ADM1`). La carpeta `geo/` del paquete trae solo la versión simplificada.
Los scripts `02`, `04`, `05` y `06` son exploración y experimentos (variantes de armonización); no son necesarios para regenerar la serie.
`pipeline/09_mapas.py` genera la figura estática (`python3 pipeline/09_mapas.py data/points_state.parquet geo/mex_adm1_full.geojson app/data/meta.json figuras/mapas.png 2012 2025`).
`pipeline/pruebas/` tiene las pruebas con Chrome sin interfaz (Playwright) con las que se verificó la app.

## Método de armonización

Unidad común: **hotspot equivalente a MODIS (Terra+Aqua)**.

1. Filtro común: solo `type == 0` (vegetación), confianza ≥ nominal (MODIS ≥ 30; VIIRS `n` o `h`).
2. Tres etapas de la serie:
   * 2000-11-01 a 2002-07-03: solo Terra, multiplicado por `k_terra_a_terra_aqua`.
   * 2002-07-04 a 2012-01-19: Terra + Aqua, peso 1.
   * 2012-01-20 a 2025-12-31: VIIRS SNPP, cada detección multiplicada por `k_viirs_a_modis`. MODIS en esa etapa se conserva como referencia y para validar.
3. Cada factor `k` es una razón por estado y mes calendario, con contracción hacia el factor nacional del mes:
   `k = (ΣMODIS + τ·k_nacional) / (ΣVIIRS + τ)`, con τ = 100. VIIRS se calibra con 2012–2019 (enero de 2012 se excluye por estar incompleto) y Terra con 2003–2011.
4. Se probaron y se descartaron: fusión de píxeles VIIRS a huella de 1 km, umbrales de FRP, separación día/noche y una ley de potencias.

### Validación (error absoluto ponderado: Σ|armonizado − MODIS observado| / ΣMODIS observado)

| | Estado × mes | Nacional × mes | Nacional × año |
|---|---|---|---|
| Un año fuera, 2012–2019 | 12.9 % | 3.7 % | 1.3 % |
| Fuera de muestra, 2020–2025 | 14.5 % | 5.4 % | 2.1 % |
| Terra → Terra+Aqua, 2003–2011 (un año fuera) | 11.5 % | 4.6 % | 3.0 % |

Las tablas completas, con las alternativas que se compararon, están en `datos_armonizados/validacion.json` y en la pestaña *Armonización* de la app.

## Columnas de los CSV

* `hotspots_armonizados_estado_dia.csv`: `fecha, clave_estado, estado, modis_terra, modis_aqua, viirs_snpp, hotspots_armonizados, fuente`
* `hotspots_armonizados_estado_mes.csv`: `anio, mes, clave_estado, estado, modis_terra, modis_aqua, viirs_snpp, hotspots_armonizados`
* `factores_calibracion.csv`: `clave_estado, estado, mes, k_viirs_a_modis, k_terra_a_terra_aqua`
* CSV de hotspots que genera la app: `fecha_utc, hora_utc, latitud, longitud, estado, sensor, frp_mw, confianza, dia_noche, peso_armonizado`. La suma de `peso_armonizado` es el conteo armonizado. Coordenadas con precisión de 0.001° y FRP de 0.1 MW. La app limita este archivo a 600,000 filas por descarga.

Los conteos crudos por sensor (`modis_terra`, `modis_aqua`, `viirs_snpp`) ya están filtrados con el criterio común del punto 1.

## Limitaciones

* **Cobertura de datos:** solo MODIS (Terra, Aqua) y VIIRS SNPP del paquete `datos_firms_bb_mexico`, hasta 2025-12-31. No incluye VIIRS NOAA-20 ni NOAA-21, ni tiempo casi real de 2026: el entorno donde se construyó no tenía acceso a los servidores de NASA.
* La etapa 2000–2002 (solo Terra, escalada) es la más incierta.
* **El factor se calibra por estado y mes, no por celda.** Agregado a estado o a país el error es bajo (tabla de arriba), pero en celdas de 0.25° la capa *Armonizado ÷ MODIS* muestra dispersión: para 2012–2025 el 90 % central de las celdas con ≥ 20 detecciones MODIS (2,048 celdas) cae entre 0.60× y 1.73×, con mediana 1.00× y mitad central entre 0.83× y 1.21×; el patrón es parecido en 2012–2019 y en 2020–2025. Conviene leer rectángulos pequeños con esa cautela.
* La deriva orbital de Terra y Aqua (visible desde ~2022) cambia la hora de paso y puede afectar la comparabilidad diurna.
* Las fechas están en UTC, como en FIRMS.
* Un hotspot no es área quemada ni una cuenta de incendios: es un píxel con anomalía térmica.
* Los rectángulos dibujados en el mapa se ajustan a celdas de 0.25°.
* Los factores se calibraron con 2012–2019; la validación fuera de muestra (2020–2025) muestra que se mantienen razonablemente estables, pero no hay garantía hacia adelante.

## Atribución

Datos: NASA FIRMS (MODIS Collection 6.x, VIIRS S-NPP 375 m). Contornos: geoBoundaries (gbOpen); consulta su licencia y atribución en geoboundaries.org.
