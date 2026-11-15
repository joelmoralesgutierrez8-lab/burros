/* Textos de la interfaz (es / en). Las cadenas son constantes del proyecto, no datos. */
window.I18N = {
es: {
  title: "Calendario de quemas",
  subtitle: "Hotspots de MODIS y VIIRS armonizados en una sola serie para México, de noviembre de 2000 a diciembre de 2025.",
  tab_explore: "Explorar", tab_harm: "Armonización", tab_about: "Datos y método",
  f_region: "Región", f_from: "Desde", f_to: "Hasta", f_metric: "Qué contar",
  p_all: "Todo", p_viirs: "Era VIIRS", p_10: "10 años", p_5: "5 años",
  m_harm: "Armonizado (equivalente MODIS)", m_modis: "MODIS observado (Terra+Aqua)", m_viirs: "VIIRS SNPP observado (sin calibrar)",
  r_all: "Todo México", r_rect: "Selección en el mapa",
  map_t: "Mapa de actividad", map_s: "Haz clic en un estado o arrastra para trazar un rectángulo. Las celdas tienen 0.25° (unos 28 km).",
  mm_state: "Estado", mm_rect: "Rectángulo", btn_all: "Todo México",
  map_layer: "Capa", map_log: "Escala logarítmica",
  layer_dens: "Densidad armonizada", layer_fact: "Factor efectivo por celda", layer_resid: "Armonizado ÷ MODIS por celda",
  map_s_fact: "Detecciones VIIRS por cada hotspot equivalente a MODIS, solo en la era VIIRS del rango. Se muestran celdas con al menos {0} detecciones VIIRS.",
  map_s_resid: "Qué tan cerca queda el conteo armonizado del MODIS observado en cada celda (1× = coincide). Solo era VIIRS; celdas con al menos {0} detecciones MODIS.",
  map_lgd_fact: "detecciones VIIRS por hotspot equivalente", map_lgd_resid: "armonizado ÷ MODIS observado",
  map_tip_fact: "detecciones VIIRS por hotspot equivalente", map_tip_viirs: "detecciones VIIRS", map_tip_harm: "hotspots armonizados", map_tip_modis: "detecciones MODIS (Terra+Aqua)", map_tip_ratio: "armonizado ÷ MODIS",
  map_nodata_layer: "Esta capa necesita días de la era VIIRS (desde el 20 de enero de 2012) dentro del rango.",
  ex_mappng: "PNG del mapa", ex_mappng_s: "La capa que se ve en el mapa",
  map_lgd: "hotspots por celda", map_dim: "Fuera de la selección",
  map_tip_cell: "Celda {0}, {1}", map_tip_total: "hotspots en el rango", map_rect_info: "Rectángulo: {0}° N a {1}° N, {2}° O a {3}° O",
  map_aria: "Mapa de México con la actividad de hotspots por celda de 0.25 grados",
  kpi_total: "Hotspots en el rango", kpi_total_h: "equivalentes MODIS", kpi_total_m: "detecciones MODIS", kpi_total_v: "detecciones VIIRS",
  kpi_month: "Mes más activo", kpi_month_d: "mediana {0}", kpi_year: "Año más activo", kpi_year_d: "{0} hotspots", kpi_year_p: "{0} hotspots (año parcial)",
  kpi_day: "Día más activo", kpi_day_d: "{0} hotspots", kpi_none: "Sin datos",
  region_line: "{0} · {1} a {2}",
  exp_t: "Descargar la selección", exp_s: "Los archivos usan la región y el rango de fechas de arriba.",
  ex_daily: "CSV diario", ex_daily_s: "Un renglón por día, con el total armonizado y cada sensor",
  ex_monthly: "CSV mensual", ex_monthly_s: "Totales por año y mes",
  ex_points: "CSV de hotspots", ex_points_s: "{0} detecciones de la selección, con peso armonizado",
  ex_points_big: "La selección tiene {0} detecciones; el máximo por archivo es {1}. Reduce la región o el rango.",
  ex_points_none: "No hay detecciones en la selección",
  ex_png: "PNG del calendario", ex_png_s: "La imagen del calendario año × mes",
  exp_note: "Las fechas están en UTC, como en FIRMS. En el CSV de hotspots, peso_armonizado es el valor que cada detección aporta a la serie (suma de pesos = hotspots armonizados).",
  saved: "Archivo guardado", savefail: "No se pudo guardar el archivo", preparing: "Preparando {0}…", loading_pts: "Leyendo detecciones {0} ({1}/{2})…",
  loading: "Cargando datos…", loaderr: "No se pudieron cargar los datos. Si abriste index.html directamente desde el disco, sírvelo con un servidor local (python3 -m http.server).",
  cal_t: "Calendario de actividad", cal_s: "Hotspots por mes y año. Cada renglón es un año; haz clic en uno para compararlo con los demás.",
  cal_count: "Conteo", cal_anom: "Anomalía", cal_table: "Ver tabla", cal_chart: "Ver gráfico",
  cal_partial: "Mes parcial dentro del rango", cal_nodata: "Sin datos de este sensor", cal_col_med: "Mediana por mes", cal_row_total: "Total anual",
  cal_lgd_count: "hotspots por mes", cal_lgd_anom: "veces la mediana del mes",
  cal_aria: "Calendario de actividad de hotspots: un renglón por año y una columna por mes",
  tip_month: "{0} {1}", tip_value: "hotspots", tip_med: "mediana del mes", tip_vs: "frente a la mediana", tip_partial: "{0} de {1} días en el rango", tip_nodata: "Sin datos de este sensor",
  tip_year_total: "total del año", tip_year_partial: "total (año parcial)", tip_sensor_terra: "MODIS Terra", tip_sensor_aqua: "MODIS Aqua", tip_sensor_snpp: "VIIRS SNPP",
  tbl_year: "Año", tbl_total: "Total",
  seas_t: "Temporada de incendios", seas_s: "La banda resume los demás años del rango; la línea es el año de referencia.",
  ref_year: "Año de referencia", seas_med: "Mediana", seas_iqr: "Rango intercuartil", seas_range: "Mínimo a máximo", seas_year: "Año {0}",
  seas_few: "Hacen falta al menos 3 años completos en el rango para trazar la banda.", seas_aria: "Hotspots por mes del año de referencia frente a la mediana de los demás años",
  seas_tip_med: "Mediana", seas_tip_iqr: "Cuartiles", seas_tip_range: "Mín. a máx.",
  daily_t: "Calendario diario de {0}", daily_s: "Cada cuadro es un día; las columnas son semanas que empiezan en lunes.",
  daily_aria: "Calendario diario del año de referencia", daily_lgd: "hotspots por día", daily_out: "Fuera del rango o sin datos",
  series_t: "Serie mensual", series_s: "Total mensual de la selección. Los fondos marcan qué sensor aporta cada etapa de la serie armonizada.",
  series_aria: "Serie mensual de hotspots", era_terra: "Terra con factor", era_ta: "Terra + Aqua", era_viirs: "VIIRS calibrado",
  month_axis: "Mes",
  harm_t: "Qué hace la armonización", harm_s: "Con VIIRS se detectan unas 4 veces más píxeles que con MODIS. Cada detección VIIRS se multiplica por un factor por estado y mes, calculado con los años 2012–2019, para que el conteo sea comparable con el de MODIS.",
  hm_obs: "MODIS observado (Terra+Aqua)", hm_cal: "VIIRS armonizado", hm_raw: "VIIRS sin calibrar", hm_show_raw: "Mostrar VIIRS sin calibrar",
  hm_calib: "Calibración", hm_oos: "Fuera de muestra", hm_aria: "Comparación mensual de MODIS observado, VIIRS armonizado y VIIRS sin calibrar",
  hm_m_raw: "VIIRS sin calibrar frente a MODIS", hm_m_raw_d: "veces más hotspots que MODIS en el traslape",
  hm_m_annual: "Error anual (VIIRS armonizado)", hm_m_annual_d: "{0} en 2012–2019 · {1} en 2020–2025",
  hm_m_month: "Error mensual", hm_m_month_d: "{0} en 2012–2019 · {1} en 2020–2025",
  hm_m_r: "Correlación mensual", hm_m_r_d: "entre MODIS observado y VIIRS armonizado",
  hm_note_state: "Las métricas se calculan para la región elegida y el traslape completo (febrero de 2012 a diciembre de 2025); no dependen del rango de fechas. El error es la suma de las diferencias absolutas dividida entre la suma de MODIS observado; en estados con pocas detecciones es mayor. Las cifras de 2012–2019 son del periodo de calibración (el factor se ajustó con esos años); las de 2020–2025 son fuera de muestra.",
  hm_tip_title: "{0} {1}",
  val_t: "Validación con el traslape", val_s: "Cada variante se calibró y se evaluó en el traslape. «Un año fuera» calibra con siete años de 2012–2019 y predice el octavo, y se repite para cada año. «Fuera de muestra» calibra con 2012–2019 y predice 2020–2025. Todas las cifras son el error absoluto ponderado: la suma de las diferencias absolutas dividida entre la suma de MODIS observado (Terra+Aqua).",
  val_levels: "Cómo se agrupa el factor", val_variants: "Qué detecciones se cuentan",
  val_col_name: "Variante", val_col_sm: "Estado × mes", val_col_nm: "Nacional × mes", val_col_an: "Nacional × año", val_col_bias: "Sesgo", val_col_r: "r mensual",
  val_loyo: "Un año fuera (2012–2019)", val_oos: "Fuera de muestra (2020–2025)", val_chosen: "elegida",
  val_terra: "Terra → Terra+Aqua (2003–2011, un año fuera): error estado × mes {0}, nacional × mes {1}, nacional × año {2}, sesgo {3}.",
  k_t: "Factores de calibración", k_s: "Hotspots MODIS equivalentes por cada detección VIIRS, según el mes. Se usa el factor del estado elegido; con otra región se muestra el nacional.",
  k_nat: "Nacional", k_aria: "Factor de calibración VIIRS a MODIS por mes",
  k_tip: "factor VIIRS → MODIS",
  about_html: `
<h3>Datos de origen</h3>
<p>Detecciones activas de incendio de NASA FIRMS: MODIS (Terra desde el 1 de noviembre de 2000, Aqua desde el 4 de julio de 2002; píxel de 1 km) y VIIRS S-NPP (desde el 20 de enero de 2012; píxel de 375 m), ya recortadas a México y hasta el 31 de diciembre de 2025. No incluye NOAA-20 ni NOAA-21, que no se pudieron descargar, ni el día de 2026 en tiempo casi real que traía el archivo de MODIS.</p>
<h3>Qué se cuenta</h3>
<p>Una detección es un píxel con anomalía térmica, no un incendio: un mismo incendio produce muchos píxeles y puede durar varios días. Se conservan las detecciones de tipo 0 (vegetación) con confianza nominal o alta (MODIS desde 30 %, VIIRS «n» y «h»), con el mismo criterio en los dos sensores. Se excluyen volcanes, fuentes estáticas (por ejemplo instalaciones petroleras) y plataformas en el mar.</p>
<h3>Unidad común</h3>
<p>El <b>hotspot equivalente MODIS</b> es lo que habrían contado Terra y Aqua juntos. Para pasar de VIIRS a esa unidad, cada detección VIIRS pesa k(estado, mes) en lugar de 1. El factor es la suma de MODIS (Terra+Aqua) entre la suma de VIIRS en el traslape 2012–2019, calculado por estado y por mes del año, y se contrae hacia el cociente nacional del mes con un peso de {tau} detecciones para que los estados con pocos hotspots no produzcan factores ruidosos. Antes de que existiera Aqua se usa el mismo procedimiento para pasar de Terra a Terra+Aqua con los años 2003–2011.</p>
<div class="era">
  <div><b>1 nov 2000 – 3 jul 2002</b><span>Terra × k de Terra. Es la etapa más incierta.</span></div>
  <div><b>4 jul 2002 – 19 ene 2012</b><span>Terra + Aqua observados, con peso 1.</span></div>
  <div><b>20 ene 2012 – 31 dic 2025</b><span>VIIRS × k de VIIRS. MODIS de estos años solo se usa para validar y en la vista «MODIS observado».</span></div>
</div>
<h3>Qué se probó</h3>
<p>Se compararon tres formas de agrupar el factor (único, por mes, por estado y mes), la fusión de píxeles VIIRS en huellas de 1 km y umbrales de FRP. Gana el factor por estado y mes sobre las detecciones sin fusionar: fusionar los píxeles duplicó el error anual porque la cantidad de píxeles VIIRS también informa el tamaño del fuego. Con un año fuera en 2012–2019 el error anual nacional es de {v_loyo_an} y con la retención 2020–2025 de {v_oos_an}; por estado y mes, {v_loyo_sm} y {v_oos_sm}. Las tablas completas están en la pestaña Armonización.</p>
<h3>Límites que conviene conocer</h3>
<ul>
<li>Los hotspots no miden superficie quemada ni intensidad. Dos meses con el mismo conteo pueden corresponder a incendios muy distintos.</li>
<li>Terra y Aqua se salen de su órbita nominal desde hace unos años: entre 2012 y 2025 la hora diurna mediana de paso de Terra pasó de 17.4 a 16.2 h UTC y la de Aqua de 20.0 a 21.0 h UTC. La calibración usa 2012–2019, antes de esa deriva, y el periodo 2020–2025 sirve de prueba fuera de muestra.</li>
<li>El error crece al bajar de escala: ronda el 1–2 % por año a nivel nacional, pero ronda el 13–15 % por estado y mes. En estados con pocos hotspots, un mes puede variar mucho.</li>
<li>La armonización supone que la razón entre sensores se mantiene estable. Un cambio de algoritmo o de régimen de quemas puede alterarla.</li>
<li>Las fechas son UTC. Los pasos nocturnos de Terra caen en el día UTC siguiente al día local.</li>
<li>Los rectángulos se ajustan a la malla de 0.25°; las celdas que cruzan un límite estatal se reparten entre los dos estados.</li>
</ul>
<h3>Reproducir y ampliar</h3>
<p>La carpeta <code>pipeline/</code> contiene los scripts que leen los archivos FIRMS, aplican los filtros, calculan los factores, validan y generan los archivos de la aplicación. Para sumar NOAA-20 y NOAA-21 basta con agregar sus archivos y repetir la calibración contra MODIS en el traslape. Los archivos <code>hotspots_armonizados_estado_dia.csv</code> y <code>hotspots_armonizados_estado_mes.csv</code> son la serie armonizada por estado.</p>
<h3>Créditos</h3>
<p>Detecciones: NASA FIRMS (LANCE, Earthdata). Límites estatales: geoBoundaries (gbOpen), simplificados para el mapa.</p>`
},
en: {
  title: "Burning calendar",
  subtitle: "MODIS and VIIRS hotspots harmonized into a single series for Mexico, from November 2000 to December 2025.",
  tab_explore: "Explore", tab_harm: "Harmonization", tab_about: "Data and method",
  f_region: "Region", f_from: "From", f_to: "To", f_metric: "What to count",
  p_all: "All", p_viirs: "VIIRS era", p_10: "10 years", p_5: "5 years",
  m_harm: "Harmonized (MODIS-equivalent)", m_modis: "MODIS observed (Terra+Aqua)", m_viirs: "VIIRS SNPP observed (uncalibrated)",
  r_all: "All of Mexico", r_rect: "Selection on the map",
  map_t: "Activity map", map_s: "Click a state or drag to draw a rectangle. Cells are 0.25° (about 28 km).",
  mm_state: "State", mm_rect: "Rectangle", btn_all: "All of Mexico",
  map_layer: "Layer", map_log: "Log scale",
  layer_dens: "Harmonized density", layer_fact: "Effective factor per cell", layer_resid: "Harmonized ÷ MODIS per cell",
  map_s_fact: "VIIRS detections per MODIS-equivalent hotspot, VIIRS era only within the range. Cells with at least {0} VIIRS detections are shown.",
  map_s_resid: "How close the harmonized count lands to observed MODIS in each cell (1× = match). VIIRS era only; cells with at least {0} MODIS detections.",
  map_lgd_fact: "VIIRS detections per equivalent hotspot", map_lgd_resid: "harmonized ÷ observed MODIS",
  map_tip_fact: "VIIRS detections per equivalent hotspot", map_tip_viirs: "VIIRS detections", map_tip_harm: "harmonized hotspots", map_tip_modis: "MODIS detections (Terra+Aqua)", map_tip_ratio: "harmonized ÷ MODIS",
  map_nodata_layer: "This layer needs days from the VIIRS era (from 20 January 2012) inside the range.",
  ex_mappng: "Map PNG", ex_mappng_s: "The layer currently on the map",
  map_lgd: "hotspots per cell", map_dim: "Outside the selection",
  map_tip_cell: "Cell {0}, {1}", map_tip_total: "hotspots in range", map_rect_info: "Rectangle: {0}° N to {1}° N, {2}° W to {3}° W",
  map_aria: "Map of Mexico with hotspot activity per 0.25 degree cell",
  kpi_total: "Hotspots in range", kpi_total_h: "MODIS-equivalent", kpi_total_m: "MODIS detections", kpi_total_v: "VIIRS detections",
  kpi_month: "Most active month", kpi_month_d: "median {0}", kpi_year: "Most active year", kpi_year_d: "{0} hotspots", kpi_year_p: "{0} hotspots (partial year)",
  kpi_day: "Most active day", kpi_day_d: "{0} hotspots", kpi_none: "No data",
  region_line: "{0} · {1} to {2}",
  exp_t: "Download the selection", exp_s: "Files use the region and date range set above.",
  ex_daily: "Daily CSV", ex_daily_s: "One row per day, with the harmonized total and each sensor",
  ex_monthly: "Monthly CSV", ex_monthly_s: "Totals by year and month",
  ex_points: "Hotspots CSV", ex_points_s: "{0} detections in the selection, with harmonized weight",
  ex_points_big: "The selection has {0} detections; the per-file maximum is {1}. Narrow the region or the range.",
  ex_points_none: "No detections in the selection",
  ex_png: "Calendar PNG", ex_png_s: "The year × month calendar as an image",
  exp_note: "Dates are UTC, as in FIRMS. In the hotspots CSV, peso_armonizado is what each detection adds to the series (weights sum to the harmonized hotspots).",
  saved: "File saved", savefail: "The file could not be saved", preparing: "Preparing {0}…", loading_pts: "Reading detections {0} ({1}/{2})…",
  loading: "Loading data…", loaderr: "The data could not be loaded. If you opened index.html straight from disk, serve it with a local server (python3 -m http.server).",
  cal_t: "Activity calendar", cal_s: "Hotspots by month and year. Each row is a year; click one to compare it with the others.",
  cal_count: "Count", cal_anom: "Anomaly", cal_table: "View table", cal_chart: "View chart",
  cal_partial: "Month partly inside the range", cal_nodata: "No data from this sensor", cal_col_med: "Median by month", cal_row_total: "Annual total",
  cal_lgd_count: "hotspots per month", cal_lgd_anom: "times the month's median",
  cal_aria: "Hotspot activity calendar: one row per year and one column per month",
  tip_month: "{0} {1}", tip_value: "hotspots", tip_med: "month's median", tip_vs: "versus the median", tip_partial: "{0} of {1} days in range", tip_nodata: "No data from this sensor",
  tip_year_total: "year total", tip_year_partial: "total (partial year)", tip_sensor_terra: "MODIS Terra", tip_sensor_aqua: "MODIS Aqua", tip_sensor_snpp: "VIIRS SNPP",
  tbl_year: "Year", tbl_total: "Total",
  seas_t: "Fire season", seas_s: "The band summarizes the other years in the range; the line is the reference year.",
  ref_year: "Reference year", seas_med: "Median", seas_iqr: "Interquartile range", seas_range: "Minimum to maximum", seas_year: "Year {0}",
  seas_few: "At least 3 complete years in the range are needed to draw the band.", seas_aria: "Hotspots per month for the reference year against the median of the other years",
  seas_tip_med: "Median", seas_tip_iqr: "Quartiles", seas_tip_range: "Min. to max.",
  daily_t: "Daily calendar for {0}", daily_s: "Each square is a day; columns are weeks starting on Monday.",
  daily_aria: "Daily calendar for the reference year", daily_lgd: "hotspots per day", daily_out: "Outside the range or no data",
  series_t: "Monthly series", series_s: "Monthly total for the selection. Backgrounds show which sensor feeds each stage of the harmonized series.",
  series_aria: "Monthly hotspot series", era_terra: "Terra with factor", era_ta: "Terra + Aqua", era_viirs: "Calibrated VIIRS",
  month_axis: "Month",
  harm_t: "What harmonization does", harm_s: "VIIRS detects about 4 times as many pixels as MODIS. Each VIIRS detection is multiplied by a factor per state and month, computed from 2012–2019, so counts are comparable with MODIS.",
  hm_obs: "MODIS observed (Terra+Aqua)", hm_cal: "Harmonized VIIRS", hm_raw: "Uncalibrated VIIRS", hm_show_raw: "Show uncalibrated VIIRS",
  hm_calib: "Calibration", hm_oos: "Out of sample", hm_aria: "Monthly comparison of observed MODIS, harmonized VIIRS and uncalibrated VIIRS",
  hm_m_raw: "Uncalibrated VIIRS versus MODIS", hm_m_raw_d: "times more hotspots than MODIS in the overlap",
  hm_m_annual: "Annual error (harmonized VIIRS)", hm_m_annual_d: "{0} in 2012–2019 · {1} in 2020–2025",
  hm_m_month: "Monthly error", hm_m_month_d: "{0} in 2012–2019 · {1} in 2020–2025",
  hm_m_r: "Monthly correlation", hm_m_r_d: "between observed MODIS and harmonized VIIRS",
  hm_note_state: "Metrics use the chosen region and the full overlap (February 2012 to December 2025); they do not depend on the date range. Error is the sum of absolute differences divided by the sum of observed MODIS; it is larger for states with few detections. Figures for 2012–2019 come from the calibration period (the factor was fitted on those years); 2020–2025 is out of sample.",
  hm_tip_title: "{0} {1}",
  val_t: "Validation on the overlap", val_s: "Each variant was calibrated and tested on the overlap. “Leave one year out” calibrates on seven years of 2012–2019 and predicts the eighth, repeated for every year. “Out of sample” calibrates on 2012–2019 and predicts 2020–2025. All figures are weighted absolute error: the sum of absolute differences divided by the sum of observed MODIS (Terra+Aqua).",
  val_levels: "How the factor is grouped", val_variants: "Which detections are counted",
  val_col_name: "Variant", val_col_sm: "State × month", val_col_nm: "National × month", val_col_an: "National × year", val_col_bias: "Bias", val_col_r: "Monthly r",
  val_loyo: "Leave one year out (2012–2019)", val_oos: "Out of sample (2020–2025)", val_chosen: "chosen",
  val_terra: "Terra → Terra+Aqua (2003–2011, leave one year out): state × month error {0}, national × month {1}, national × year {2}, bias {3}.",
  k_t: "Calibration factors", k_s: "MODIS-equivalent hotspots per VIIRS detection, by month. The chosen state's factor is used; for other regions the national one is shown.",
  k_nat: "National", k_aria: "VIIRS to MODIS calibration factor by month",
  k_tip: "VIIRS → MODIS factor",
  about_html: `
<h3>Source data</h3>
<p>NASA FIRMS active-fire detections: MODIS (Terra from 1 November 2000, Aqua from 4 July 2002; 1 km pixel) and VIIRS S-NPP (from 20 January 2012; 375 m pixel), already clipped to Mexico and running to 31 December 2025. NOAA-20 and NOAA-21 are not included because they could not be downloaded, and neither is the single near-real-time day of 2026 that came with the MODIS file.</p>
<h3>What is counted</h3>
<p>A detection is a pixel with a thermal anomaly, not a fire: one fire produces many pixels and can last several days. Detections are kept when type is 0 (vegetation fire) and confidence is nominal or high (MODIS 30 or above, VIIRS “n” and “h”), the same rule for both sensors. Volcanoes, static sources (such as oil facilities) and offshore platforms are excluded.</p>
<h3>Common unit</h3>
<p>The <b>MODIS-equivalent hotspot</b> is what Terra and Aqua together would have counted. To convert VIIRS into that unit, each VIIRS detection weighs k(state, month) instead of 1. The factor is the sum of MODIS (Terra+Aqua) divided by the sum of VIIRS over the 2012–2019 overlap, computed by state and calendar month and shrunk toward the national monthly ratio with a weight of {tau} detections so states with few hotspots do not produce noisy factors. Before Aqua existed, the same procedure converts Terra into Terra+Aqua using 2003–2011.</p>
<div class="era">
  <div><b>1 Nov 2000 – 3 Jul 2002</b><span>Terra × Terra factor. The most uncertain stage.</span></div>
  <div><b>4 Jul 2002 – 19 Jan 2012</b><span>Terra + Aqua as observed, weight 1.</span></div>
  <div><b>20 Jan 2012 – 31 Dec 2025</b><span>VIIRS × VIIRS factor. MODIS in these years is only used for validation and in the “MODIS observed” view.</span></div>
</div>
<h3>What was tested</h3>
<p>Three ways to group the factor (single, by month, by state and month), merging VIIRS pixels into 1 km footprints, and FRP thresholds were compared. The state-and-month factor on unmerged detections wins: merging pixels doubled the annual error because the number of VIIRS pixels also carries fire size. With leave-one-year-out on 2012–2019 the national annual error is {v_loyo_an}, and on the 2020–2025 holdout it is {v_oos_an}; by state and month, {v_loyo_sm} and {v_oos_sm}. Full tables are in the Harmonization tab.</p>
<h3>Limits worth knowing</h3>
<ul>
<li>Hotspots do not measure burned area or intensity. Two months with the same count can be very different fires.</li>
<li>Terra and Aqua have been drifting off their nominal orbit: between 2012 and 2025 the median daytime pass time of Terra moved from 17.4 to 16.2 h UTC and that of Aqua from 20.0 to 21.0 h UTC. Calibration uses 2012–2019, before the drift, and 2020–2025 serves as the out-of-sample test.</li>
<li>Error grows at finer scales: about 1–2 % per year nationally, but about 13–15 % per state and month. In states with few hotspots a month can vary a lot.</li>
<li>Harmonization assumes the ratio between sensors stays stable. An algorithm change or a change in burning practices can alter it.</li>
<li>Dates are UTC. Night passes of Terra fall on the UTC day after the local day.</li>
<li>Rectangles snap to the 0.25° grid; cells crossing a state border are split between the two states.</li>
</ul>
<h3>Reproduce and extend</h3>
<p>The <code>pipeline/</code> folder holds the scripts that read the FIRMS files, apply the filters, compute the factors, validate and build the app files. To add NOAA-20 and NOAA-21, add their files and repeat the calibration against MODIS on the overlap. The files <code>hotspots_armonizados_estado_dia.csv</code> and <code>hotspots_armonizados_estado_mes.csv</code> are the harmonized series by state.</p>
<h3>Credits</h3>
<p>Detections: NASA FIRMS (LANCE, Earthdata). State boundaries: geoBoundaries (gbOpen), simplified for the map.</p>`
}
};
window.I18N.es.months = ["enero","febrero","marzo","abril","mayo","junio","julio","agosto","septiembre","octubre","noviembre","diciembre"];
window.I18N.es.mon = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"];
window.I18N.es.dow = ["L","M","X","J","V","S","D"];
window.I18N.en.months = ["January","February","March","April","May","June","July","August","September","October","November","December"];
window.I18N.en.mon = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
window.I18N.en.dow = ["M","T","W","T","F","S","S"];
