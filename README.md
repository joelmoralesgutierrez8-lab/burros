# Calendario de quemas — MODIS + VIIRS armonizados (México, 2000–2025)

Proyecto para el reto **Harmonization of MODIS and VIIRS Hot Spots** de **NASA Space Apps Challenge 2026** (Equipo **Burros Biónicos** — IPN ESCOM).

🌐 **Aplicación Web Interactiva (GitHub Pages):** [Abrir Calendario de Quemas](https://joelmoralesgutierrez8-lab.github.io/burros/)  
📄 **Documento Matemático y Estadístico Extenso (PDF):** [`Extenso_procedimiento_matematico_y_estadistico.pdf`](./Extenso_procedimiento_matematico_y_estadistico.pdf)

---

## Estructura del Repositorio

| Carpeta / Archivo | Descripción |
|---|---|
| [`Calendario de quemas — MODIS + VIIRS armonizados/`](./Calendario%20de%20quemas%20%E2%80%94%20MODIS%20+%20VIIRS%20armonizados/) | **Aplicación web estática completa** (Explorador, Armonización, Pronóstico 2026 e Información). Sin dependencias externas. |
| [`Extenso_proyecto_LaTeX/extenso_latex/`](./Extenso_proyecto_LaTeX/extenso_latex/) | Código fuente en LaTeX, figuras y scripts de validación reproducible del documento matemático y estadístico. |
| [`calendario_quemas/calendario_quemas/`](./calendario_quemas/calendario_quemas/) | Pipeline en Python (`01_load.py` a `10_empaquetar_app.py`), series armonizadas en CSV, factores de calibración y pruebas automatizadas. |
| [`Extenso_procedimiento_matematico_y_estadistico.pdf`](./Extenso_procedimiento_matematico_y_estadistico.pdf) | Memoria técnica compilada con toda la deducción matemática, validación fuera de muestra y pronóstico. |

---

## Resumen de Resultados Clave

1. **Armonización (2000–2025):** Unidad común en *hotspots equivalentes a MODIS (Terra+Aqua)* mediante estimador por razón condicional con contracción empírico-bayesiana ($\tau = 100$) por estado y mes:
   $$\widetilde{k}_{m,s} = \frac{\sum_y M_{y,m,s} + \tau\,\widehat{k}_{\mathrm{nac},m}}{\sum_y V_{y,m,s} + \tau}$$
2. **Validación (WAPE — Error Porcentual Absoluto Ponderado):**

| Ejercicio | Estado × mes | Nacional × mes | Nacional × año |
|---|---:|---:|---:|
| Un año fuera (LOYO, 2012–2019) | 12.9 % | 3.7 % | **1.3 %** |
| Fuera de muestra (2020–2025) | 14.5 % | 5.4 % | **2.1 %** |
| Terra → Terra+Aqua (LOYO, 2003–2011) | 11.5 % | 4.6 % | **3.0 %** |

3. **Pronóstico:** Climatología de ventana móvil ($\pm 14$ días, $K=12$ años) con ajuste de nivel reciente ($L=28$ días) y decaimiento exponencial ($\vartheta = 60$ días), acompañado de intervalos empíricos al 80 % validados con *backtesting* en 314 orígenes semanales (2020–2025).

---

## Cómo abrir la aplicación web en tu computadora

```bash
cd "Calendario de quemas — MODIS + VIIRS armonizados"
python -m http.server 8000
```
Luego abre en tu navegador: **http://localhost:8000**
