import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Inicializar presentación panorámica 16:9
prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

# Paleta extraída directamente de tu imagen de referencia (NASA FIRMS / Earthdata)
COLOR_BG = RGBColor(11, 14, 19)          # #0B0E13 Fondo oscuro espacial
COLOR_PANEL = RGBColor(18, 24, 34)       # #121822 Paneles HUD
COLOR_CRIMSON = RGBColor(142, 24, 43)    # #8E182B Rojo carmesí institucional
COLOR_FLAME = RGBColor(230, 57, 70)      # #E63946 Rojo térmico / acento
COLOR_AMBER = RGBColor(244, 162, 97)     # #F4A261 Ámbar / Dorado (2012-2025)
COLOR_WHITE = RGBColor(245, 247, 250)    # #F5F7FA Blanco puro
COLOR_GRAY = RGBColor(176, 184, 196)     # #B0B8C4 Gris técnico
COLOR_LINE = RGBColor(55, 65, 81)        # #374151 Líneas divisoras

def aplicar_tema_nasa(slide, titulo, subtitulo, num_slide):
    # Fondo oscuro
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG

    # Barra lateral izquierda estilo HUD de satélite (como en tu imagen)
    hud = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.18), Inches(1.8), Inches(0.42), Inches(3.6))
    hud.fill.solid()
    hud.fill.fore_color.rgb = COLOR_PANEL
    hud.line.color.rgb = COLOR_LINE
    hud.line.width = Pt(1)

    # Indicador activo en el HUD según el número de diapositiva
    pos_y = 2.0 + ((num_slide - 2) % 5) * 0.65
    activo = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.22), Inches(pos_y), Inches(0.34), Inches(0.45))
    activo.fill.solid()
    activo.fill.fore_color.rgb = COLOR_CRIMSON
    activo.line.fill.background()

    # Franja superior con acento diagonal carmesí
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.35), Inches(0.08), Inches(0.85))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = COLOR_FLAME
    top_bar.line.fill.background()

    # Encabezado técnico superior derecho
    tb_tag = slide.shapes.add_textbox(Inches(9.2), Inches(0.32), Inches(3.8), Inches(0.4))
    tf_tag = tb_tag.text_frame
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = "NASA SPACE APPS 2026  |  BURROS BIOLÓGICOS"
    p_tag.alignment = PP_ALIGN.RIGHT
    p_tag.font.name = "Consolas"
    p_tag.font.size = Pt(10)
    p_tag.font.color.rgb = COLOR_AMBER

    # Título principal de la diapositiva
    tb_title = slide.shapes.add_textbox(Inches(1.0), Inches(0.3), Inches(8.5), Inches(0.55))
    tf_title = tb_title.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = titulo
    p_title.font.name = "Segoe UI"
    p_title.font.size = Pt(26)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_WHITE

    # Subtítulo
    tb_sub = slide.shapes.add_textbox(Inches(1.0), Inches(0.82), Inches(11.5), Inches(0.4))
    tf_sub = tb_sub.text_frame
    tf_sub.word_wrap = True
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = subtitulo
    p_sub.font.name = "Segoe UI"
    p_sub.font.size = Pt(14)
    p_sub.font.italic = True
    p_sub.font.color.rgb = COLOR_AMBER

    # Línea divisoria horizontal sutil
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(1.28), Inches(11.9), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = COLOR_LINE
    line.line.fill.background()

    # Pie de página con número de diapositiva y etiqueta FIRMS
    footer = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(7.12), Inches(13.333), Inches(0.38))
    footer.fill.solid()
    footer.fill.fore_color.rgb = COLOR_CRIMSON
    footer.line.fill.background()

    tb_foot = slide.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(12.0), Inches(0.3))
    tf_foot = tb_foot.text_frame
    p_foot = tf_foot.paragraphs[0]
    p_foot.text = f"HARMONIZATION OF MODIS & VIIRS HOT SPOTS (MÉXICO 2012–2025)          SLIDE 0{num_slide} / 08"
    p_foot.alignment = PP_ALIGN.RIGHT
    p_foot.font.name = "Consolas"
    p_foot.font.size = Pt(10)
    p_foot.font.bold = True
    p_foot.font.color.rgb = COLOR_WHITE

def agregar_tarjeta(slide, left, top, width, height, titulo_card, bullets, acento=COLOR_FLAME):
    card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = COLOR_PANEL
    card.line.color.rgb = COLOR_LINE
    card.line.width = Pt(1)

    # Borde izquierdo de color
    borde = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(0.07), height)
    borde.fill.solid()
    borde.fill.fore_color.rgb = acento
    borde.line.fill.background()

    tb = slide.shapes.add_textbox(left + Inches(0.22), top + Inches(0.15), width - Inches(0.35), height - Inches(0.25))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = titulo_card
    p0.font.name = "Segoe UI"
    p0.font.size = Pt(16)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_WHITE
    p0.space_after = Pt(8)

    for b in bullets:
        p = tf.add_paragraph()
        p.text = f"▸ {b}"
        p.font.name = "Segoe UI"
        p.font.size = Pt(13)
        p.font.color.rgb = COLOR_GRAY
        p.space_after = Pt(6)

# ==============================================================================
# SLIDE 1: PORTADA (Usa tu imagen de referencia directamente si existe)
# ==============================================================================
s1 = prs.slides.add_slide(blank_layout)
if os.path.exists("portada_ref.png"):
    s1.shapes.add_picture("portada_ref.png", Inches(0), Inches(0), width=Inches(13.333), height=Inches(7.5))
else:
    bg = s1.background
    bg.fill.solid()
    bg.fill.fore_color.rgb = COLOR_BG
    agregar_tarjeta(
        s1, Inches(1.2), Inches(1.8), Inches(10.9), Inches(3.8),
        "Armonización Multi-Sensor de Puntos Críticos (MODIS & VIIRS) para la Gestión Preventiva del Fuego",
        [
            "Calendario Histórico Armonizado y Pronóstico Espaciotemporal de Incendios en México (2012–2025)",
            "Equipo: Burros Biológicos  |  IPN - ESCOM",
            "Desafío: Harmonization of MODIS and VIIRS Hot Spots – NASA Space Apps Challenge 2026"
        ],
        acento=COLOR_CRIMSON
    )

# ==============================================================================
# SLIDE 2: EL PROBLEMA
# ==============================================================================
s2 = prs.slides.add_slide(blank_layout)
aplicar_tema_nasa(
    s2,
    "1. El Problema: Un Registro Histórico Fracturado",
    "Más de dos décadas de datos satelitales de incendios que no pueden compararse directamente",
    2
)
agregar_tarjeta(
    s2, Inches(1.0), Inches(1.6), Inches(5.7), Inches(2.4),
    "Transición Tecnológica (MODIS → VIIRS)",
    [
        "MODIS (Terra y Aqua, 1 km) se acerca al final de su vida operativa.",
        "VIIRS (Suomi-NPP, NOAA-20 y NOAA-21, 375 m) ofrece mayor detalle espacial.",
        "Diferentes canales infrarrojos (MIR/TIR) y escalas de confianza."
    ],
    acento=COLOR_AMBER
)
agregar_tarjeta(
    s2, Inches(7.1), Inches(1.6), Inches(5.8), Inches(2.4),
    "El Sesgo de Resolución (Distribution Drift)",
    [
        "El área de píxel de VIIRS es ~7 veces más fina que la de MODIS.",
        "VIIRS detecta quemas pequeñas invisibles para MODIS y fragmenta fuegos grandes.",
        "Unirlos sin armonizar infla artificialmente los conteos históricos."
    ],
    acento=COLOR_FLAME
)
agregar_tarjeta(
    s2, Inches(1.0), Inches(4.3), Inches(11.9), Inches(2.4),
    "Impacto Operativo en la Gestión del Fuego",
    [
        "Sin una línea base consistente, Protección Civil y brigadistas no pueden distinguir si una temporada es realmente anómala o producto del cambio de sensor.",
        "Se requiere una metodología científica para que el sensor de origen deje de importar."
    ],
    acento=COLOR_CRIMSON
)

# ==============================================================================
# SLIDE 3: NUESTRA SOLUCIÓN
# ==============================================================================
s3 = prs.slides.add_slide(blank_layout)
aplicar_tema_nasa(
    s3,
    "2. Nuestra Solución: De Datos Crudos a Inteligencia Preventiva",
    "Pipeline científico de armonización multi-sensor + Aplicación web interactiva con datos abiertos",
    3
)
agregar_tarjeta(
    s3, Inches(1.0), Inches(1.7), Inches(3.7), Inches(4.9),
    "Pilar 1: Motor de Armonización",
    [
        "Ingesta masiva en Parquet de MODIS (2012–2025) y VIIRS.",
        "Homologación térmica en Kelvin (ΔT) y niveles de confianza.",
        "Cercado geográfico (~1.11 km/día) que elimina duplicados multi-satélite."
    ],
    acento=COLOR_FLAME
)
agregar_tarjeta(
    s3, Inches(5.1), Inches(1.7), Inches(3.7), Inches(4.9),
    "Pilar 2: Calendario de Quemas",
    [
        "Matriz visual interactiva Año × Mes (Burning Activity Calendar).",
        "Identificación inmediata de estacionalidad y periodos críticos.",
        "Comparativa de la actividad actual frente a la mediana histórica."
    ],
    acento=COLOR_AMBER
)
agregar_tarjeta(
    s3, Inches(9.2), Inches(1.7), Inches(3.7), Inches(4.9),
    "Pilar 3: Ciencia Abierta (CSV)",
    [
        "Generación de base maestra limpia: hotspots_harmonized.csv.",
        "Descarga directa desde la aplicación web para análisis SIG.",
        "Trazabilidad total bajo estándares de NASA Earthdata / FIRMS."
    ],
    acento=COLOR_CRIMSON
)

# ==============================================================================
# SLIDE 4: INGENIERÍA DE DATOS Y ARMONIZACIÓN
# ==============================================================================
s4 = prs.slides.add_slide(blank_layout)
aplicar_tema_nasa(
    s4,
    "3. Ingeniería de Datos y Armonización (Metodología CRISP-DM)",
    "Estandarización física, espacial y temporal ejecutada en Python 3.12",
    4
)
agregar_tarjeta(
    s4, Inches(1.0), Inches(1.6), Inches(6.2), Inches(5.1),
    "Pipeline de Armonización Paso a Paso",
    [
        "Esquemas Térmicos: Unificación de brightness/bright_ti4 (temp_brillo) y bright_t31/bright_ti5 (temp_brillo_sec) + gradiente ΔT.",
        "Estandarización de Confianza: Mapeo de escala continua MODIS (0–100%) a categorías ordinales VIIRS (low, nominal, high).",
        "Cercado Geográfico (0.01° ≈ 1.11 km): Agrupación diaria por celda espacial que resuelve pasadas múltiples (Terra, Aqua, S-NPP, N20, N21).",
        "Priorización Física: Conserva el registro de mayor resolución (375 m) y mayor Potencia Radiativa del Fuego (FRP)."
    ],
    acento=COLOR_FLAME
)
agregar_tarjeta(
    s4, Inches(7.5), Inches(1.6), Inches(5.4), Inches(5.1),
    "Evidencia: Antes vs. Después",
    [
        "SIN ARMONIZAR: Salto artificial abrupto en el conteo de focos al incorporarse VIIRS (375 m).",
        "ARMONIZADO: Serie continua y físicamente coherente en celdas de 1.11 km².",
        "Espacio reservado para insertar tu gráfica comparativa de series de tiempo (2012–2025)."
    ],
    acento=COLOR_AMBER
)

# ==============================================================================
# SLIDE 5: MACHINE LEARNING Y MODELADO PREDICTIVO
# ==============================================================================
s5 = prs.slides.add_slide(blank_layout)
aplicar_tema_nasa(
    s5,
    "4. Machine Learning y Modelado Espaciotemporal",
    "Reconstrucción histórica y pronóstico preventivo con restricciones físicas",
    5
)
agregar_tarjeta(
    s5, Inches(1.0), Inches(1.6), Inches(5.7), Inches(5.1),
    "Armonización Histórica (HGB + Filtro Hurdle)",
    [
        "HistGradientBoostingRegressor con pérdida de Poisson regularizada (L2).",
        "Filtro físico tipo Hurdle: si actividad MODIS = 0, predicción = 0 (elimina falsos positivos).",
        "Acotamiento superior físico para evitar extrapolaciones irreales.",
        "Ajuste validado de R² ≈ 0.97 en la ventana de solapamiento."
    ],
    acento=COLOR_CRIMSON
)
agregar_tarjeta(
    s5, Inches(7.1), Inches(1.6), Inches(5.8), Inches(5.1),
    "Clasificación y Pronóstico Futuro",
    [
        "Clasificador LightGBM para evaluación de confianza y severidad térmica (FRP, ΔT).",
        "Ingeniería de características temporales: variables cíclicas (seno/coseno del mes) y rezagos históricos (lags).",
        "División cronológica estricta (Train / Val / Test) para proyectar riesgo sin fuga de datos."
    ],
    acento=COLOR_AMBER
)

# ==============================================================================
# SLIDE 6: DEMOSTRACIÓN DE LA APLICACIÓN WEB
# ==============================================================================
s6 = prs.slides.add_slide(blank_layout)
aplicar_tema_nasa(
    s6,
    "5. Demostración de la Aplicación Web (Dashboard)",
    "Interfaz institucional inspirada en NASA Earthdata / FIRMS para alerta temprana",
    6
)
agregar_tarjeta(
    s6, Inches(1.0), Inches(1.6), Inches(4.5), Inches(5.1),
    "Funcionalidades Clave",
    [
        "Mapa Interactivo Geoespacial: Visualización de focos activos con filtros por satélite, fecha y confianza.",
        "Calendario en Llamas: Heatmap Año × Mes que destaca temporadas pico (marzo–mayo).",
        "Exportación Directa: Descarga instantánea de hotspots_harmonized.csv filtrado."
    ],
    acento=COLOR_FLAME
)
agregar_tarjeta(
    s6, Inches(5.8), Inches(1.6), Inches(7.1), Inches(5.1),
    "Vista de la Plataforma en Operación",
    [
        "Inserta aquí 2 o 3 capturas de pantalla reales de tu Dashboard en Streamlit:",
        "1) Mapa de focos de calor en México.",
        "2) Matriz de Calor del Calendario de Actividad de Quemas.",
        "3) Panel de descarga CSV y métricas de severidad."
    ],
    acento=COLOR_CRIMSON
)

# ==============================================================================
# SLIDE 7: IMPACTO SOCIAL Y CASOS DE USO
# ==============================================================================
s7 = prs.slides.add_slide(blank_layout)
aplicar_tema_nasa(
    s7,
    "6. Impacto Social y Aplicaciones Operativas",
    "Traduciendo observaciones orbitales en decisiones oportunas para proteger vidas y ecosistemas",
    7
)
agregar_tarjeta(
    s7, Inches(1.0), Inches(1.7), Inches(3.7), Inches(4.9),
    "Protección Civil y Brigadistas",
    [
        "Anticipación de ventanas críticas de riesgo antes de que escalen a megaincendios.",
        "Optimización en el despliegue preventivo de brigadas y recursos hídricos."
    ],
    acento=COLOR_FLAME
)
agregar_tarjeta(
    s7, Inches(5.1), Inches(1.7), Inches(3.7), Inches(4.9),
    "Gestores de Tierras y Agro",
    [
        "Monitoreo de quemas agrícolas estacionales frente a incendios forestales atípicos.",
        "Evaluación histórica por región para planes de manejo de combustible."
    ],
    acento=COLOR_AMBER
)
agregar_tarjeta(
    s7, Inches(9.2), Inches(1.7), Inches(3.7), Inches(4.9),
    "Comunidad Científica",
    [
        "Serie temporal continua (2012–2025) libre de sesgo por cambio de sensor.",
        "Dataset estandarizado listo para estudios climáticos y de biodiversidad."
    ],
    acento=COLOR_CRIMSON
)

# ==============================================================================
# SLIDE 8: CONCLUSIONES Y TRABAJO FUTURO
# ==============================================================================
s8 = prs.slides.add_slide(blank_layout)
aplicar_tema_nasa(
    s8,
    "7. Conclusiones, Limitaciones y Trabajo Futuro",
    "Hoja de ruta para escalar hacia un sistema nacional de monitoreo en tiempo casi real",
    8
)
agregar_tarjeta(
    s8, Inches(1.0), Inches(1.6), Inches(5.7), Inches(2.4),
    "Logros Alcanzados",
    [
        "Base maestra armonizada sin doble conteo multi-satélite (MODIS + VIIRS).",
        "Calendario de actividad de quemas funcional y modelos validados."
    ],
    acento=COLOR_AMBER
)
agregar_tarjeta(
    s8, Inches(7.1), Inches(1.6), Inches(5.8), Inches(2.4),
    "Limitaciones Técnicas",
    [
        "La teledetección óptica/térmica se ve atenuada por nubosidad densa.",
        "Incendios de muy corta duración pueden ocurrir entre pasadas orbitales."
    ],
    acento=COLOR_GRAY
)
agregar_tarjeta(
    s8, Inches(1.0), Inches(4.3), Inches(11.9), Inches(2.4),
    "Próximos Pasos (Escalabilidad)",
    [
        "Ingesta automática Near Real-Time (NRT) conectada vía API oficial de NASA FIRMS con MAP_KEY.",
        "Cruce geoespacial con límites municipales, áreas naturales protegidas y redes viales para índices locales de vulnerabilidad."
    ],
    acento=COLOR_FLAME
)

output_file = "Presentacion_Burros_Biologicos_NASA_2026.pptx"
prs.save(output_file)
print(f"Presentación generada exitosamente: {output_file}")