"""Dibuja el diagrama de arquitectura del prototipo (Figura 1 del informe)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

AZUL, FONDO, VERDE, AMBAR, GRIS = "#1E3A8A", "#EEF4FC", "#E7F5EC", "#FDF3E1", "#8C8C8C"
ETAPAS = [
    (
        "1. FUENTES OFICIALES",
        "Agencia Andina (Sunedu) · portal UNDC · PuntoEdu PUCP",
        "gob.pe (MINEDU, SUNEDU) bloqueó nuestras herramientas automatizadas (HTTP 418)",
        FONDO,
    ),
    (
        "2. CAPTURA CONTROLADA",
        "Manual: agregar_noticias.py · Semiautomática: capturar_candidatas.py",
        "API pública de WordPress, sin extraer HTML; las candidatas entran como «Pendiente»",
        FONDO,
    ),
    (
        "3. VALIDACIÓN (datos.py)",
        "Campos obligatorios · fecha AAAA-MM-DD · URL http(s) única · estado permitido",
        "Doble control: en Python y con restricciones CHECK de SQLite",
        FONDO,
    ),
    (
        "4. ALMACENAMIENTO",
        "SQLite oes.db → tabla noticias",
        "con estado, verificado_por, fecha de captura y fecha de verificación",
        FONDO,
    ),
    (
        "5. REVISIÓN HUMANA (Bandeja)",
        "Resumen propio + quién verificó + confirmación de titular y fecha",
        "Solo las noticias aprobadas cuentan en los indicadores",
        AMBAR,
    ),
    (
        "6. ANÁLISIS (analisis.py)",
        "Temas por palabras clave · alertas · índice de trazabilidad 0-100",
        "Reglas visibles y explicables, sin servicios externos",
        VERDE,
    ),
    (
        "7. TABLERO Y DECISIONES (app.py)",
        "Filtros · indicadores · radar de temas · ficha · exportación CSV",
        "Decisiones de marketing educativo con fuente verificable",
        VERDE,
    ),
]

fig, ax = plt.subplots(figsize=(10, 13.6), dpi=200)
ax.set_xlim(0, 10)
ax.set_ylim(0, 13.6)
ax.axis("off")
alto, separacion, y = 1.42, 0.36, 13.45
for i, (titulo, linea1, linea2, color) in enumerate(ETAPAS):
    y0 = y - alto
    ax.add_patch(
        FancyBboxPatch((0.5, y0), 9.0, alto, boxstyle="round,pad=0.02,rounding_size=0.12", fc=color, ec=AZUL, lw=1.8)
    )
    ax.text(5, y0 + alto * 0.73, titulo, ha="center", va="center", fontsize=13, fontweight="bold", color=AZUL)
    ax.text(5, y0 + alto * 0.44, linea1, ha="center", va="center", fontsize=10.2)
    ax.text(5, y0 + alto * 0.17, linea2, ha="center", va="center", fontsize=9.3, color="#404040", style="italic")
    if i < len(ETAPAS) - 1:
        ax.annotate(
            "",
            xy=(5, y0 - separacion + 0.03),
            xytext=(5, y0 - 0.03),
            arrowprops={"arrowstyle": "-|>", "color": AZUL, "lw": 1.8},
        )
    y = y0 - separacion

ax.add_patch(
    FancyBboxPatch(
        (0.5, 0.08), 9.0, 0.72, boxstyle="round,pad=0.02,rounding_size=0.12", fc="white", ec=GRIS, lw=1.4, ls="--"
    )
)
ax.text(
    5,
    0.56,
    "Extensiones propuestas, no implementadas",
    ha="center",
    va="center",
    fontsize=10.5,
    fontweight="bold",
    color=GRIS,
)
ax.text(
    5,
    0.29,
    "Transparencia presupuestal · condiciones de calidad · resúmenes con IA revisados por una persona",
    ha="center",
    va="center",
    fontsize=9.3,
    color=GRIS,
)
fig.tight_layout()
fig.savefig(Path(__file__).with_name("figura_arquitectura.png"))
print("Diagrama generado: evidencias/figura_arquitectura.png")
