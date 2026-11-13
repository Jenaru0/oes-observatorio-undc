# OES académico — Práctica Guiada N.° 08 (v2)

**Aplicación en línea:** https://jenaru0-oes-observatorio-undc-app-o1musb.streamlit.app

Prototipo local de un **Observatorio de Educación Superior** con Python, SQLite y Streamlit
(curso Inteligencia Artificial Aplicada al Marketing Digital, UNDC, 2026-II).

La versión 2 parte del código de la guía (commit inicial) y agrega:

- **Bandeja de revisión** («humano en el circuito»): `capturar_candidatas.py` trae noticias de las API
  públicas de los portales como *Pendiente*; una persona las aprueba con un resumen propio.
- **Radar de temas y alertas** para marketing educativo, con reglas de palabras clave visibles.
- **Índice de trazabilidad (0-100)** por noticia.
- Validación doble (Python + `CHECK` de SQLite), conexiones que siempre se cierran, 24 pruebas
  automáticas, lint con ruff y evidencias reproducibles con un solo comando.

## Ejecutar

```bash
python -m venv .venv
.venv\Scripts\activate                 # Windows
pip install -r requirements.txt
python preparar_datos.py               # crea oes.db con los 3 ejemplos de la guía
python agregar_noticias.py             # agrega 4 noticias reales verificadas (12/11/2026)
python capturar_candidatas.py          # opcional: trae candidatas a la Bandeja de revisión
streamlit run app.py                   # abre http://localhost:8501
```

## Calidad

```bash
pip install -r requirements-dev.txt
python -m pytest                       # 24 pruebas: datos, análisis, captura y tablero (AppTest)
ruff check . && ruff format --check .
python evidencias/generar_evidencias.py   # con el tablero corriendo: regenera P1–P6 y la bandeja
```

## Archivos

| Archivo | Qué hace |
|---|---|
| `datos.py` | Esquema, validación, inserción, lectura y revisión de noticias (único acceso a la base) |
| `analisis.py` | Temas por palabras clave, alertas, índice de trazabilidad, filtros y radar |
| `app.py` | Tablero: filtros, indicadores, panorama, noticias con ficha, bandeja y metodología |
| `preparar_datos.py` | Paso 4: crea la base con los 3 ejemplos de la guía |
| `agregar_noticias.py` | Paso 7: 4 noticias reales con URL directa, titular y fecha verificados |
| `capturar_candidatas.py` | Captura semiautomática desde API públicas de WordPress (UNDC y PUCP) |
| `.streamlit/config.toml` | Tema visual: minimalismo suizo, claro y de alto contraste |
| `tests/` | Pruebas automáticas (pytest + `streamlit.testing.v1.AppTest`) |
| `evidencias/` | Capturas y salidas de P1–P6 y de la bandeja, CSV exportados y diagrama |

Los 3 registros de ejemplo apuntan a portadas institucionales y tienen trazabilidad 0:
deben retirarse antes de cualquier uso institucional. La base `oes.db` se incluye en el repositorio
como base de demostración, para que la versión en línea muestre los mismos datos.
