"""Regenera TODAS las evidencias en orden, desde una base vacía.

Requisito: el tablero corriendo en otra terminal (streamlit run app.py --server.headless true).
Uso:  python evidencias/generar_evidencias.py
"""

import sqlite3
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
EVID = RAIZ / "evidencias"
DB = RAIZ / "oes.db"


def correr(*args) -> str:
    resultado = subprocess.run(
        [sys.executable, *args], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8", check=True
    )
    return resultado.stdout


def consulta(sql: str) -> str:
    con = sqlite3.connect(DB)
    try:
        return "\n".join(f"  {fila}" for fila in con.execute(sql))
    finally:
        con.close()


def guardar(nombre: str, texto: str) -> None:
    (EVID / nombre).write_text(texto, encoding="utf-8")
    print(texto)


DB.unlink(missing_ok=True)

# P1: la carga doble no duplica
guardar(
    "P1_carga_doble.txt",
    "$ python preparar_datos.py   (1.a ejecución)\n"
    + correr("preparar_datos.py")
    + "\n$ python preparar_datos.py   (2.a ejecución)\n"
    + correr("preparar_datos.py")
    + "\n$ Registros en la base\n"
    + consulta("SELECT id, institucion, estado, url FROM noticias")
    + "\n",
)
print(correr("evidencias/capturar_evidencias.py", "inicial"))  # P0, P2–P5

# P6: noticias reales verificadas
guardar(
    "P6_carga_noticias_reales.txt",
    "$ python agregar_noticias.py\n"
    + correr("agregar_noticias.py")
    + "\n$ Noticias verificadas\n"
    + consulta("SELECT id, fecha, institucion, verificado_por, url FROM noticias WHERE estado = 'Verificada'")
    + "\n",
)
print(correr("evidencias/capturar_evidencias.py", "final"))

# Novedad: captura semiautomática y bandeja de revisión
guardar(
    "N0_captura_candidatas.txt",
    "$ python capturar_candidatas.py\n"
    + correr("capturar_candidatas.py")
    + "\n$ Noticias pendientes de revisión\n"
    + consulta("SELECT id, fecha, institucion, titulo FROM noticias WHERE estado = 'Pendiente'")
    + "\n",
)
print(correr("evidencias/capturar_evidencias.py", "bandeja"))
print(correr("evidencias/diagrama_arquitectura.py"))
