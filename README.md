# OES académico — Práctica Guiada N.° 08

Prototipo local de un Observatorio de Educación Superior con Python, SQLite y Streamlit
(curso Inteligencia Artificial Aplicada al Marketing Digital, UNDC, 2026-II).

## Ejecutar

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python preparar_datos.py        # crea oes.db con 3 registros DEMOSTRATIVOS
python agregar_noticias.py      # agrega 4 noticias reales verificadas (12/11/2026)
streamlit run app.py            # abre http://localhost:8501
```

## Archivos

| Archivo | Qué hace |
|---|---|
| `preparar_datos.py` | Crea la tabla `noticias` y carga 3 ejemplos (código de la guía, sin cambios) |
| `app.py` | Tablero: filtros, 3 indicadores, gráfico, tabla y exportación CSV (código de la guía, sin cambios) |
| `agregar_noticias.py` | Paso 7: 4 noticias reales con URL directa, titular y fecha verificados |
| `oes.db` | Base SQLite con los 7 registros (3 de ejemplo + 4 reales) |
| `evidencias/` | Capturas y salidas de las pruebas P1–P6, CSV exportados y diagrama de arquitectura |
| `evidencias/capturar_evidencias.py` | Maneja el tablero con Playwright (Edge) para generar las capturas de P2–P6 |

Los 3 registros de ejemplo apuntan a portadas institucionales, no a noticias concretas:
deben retirarse antes de cualquier uso institucional.
