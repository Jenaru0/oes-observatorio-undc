"""Acceso a la base del observatorio: esquema, validación e inserción de noticias."""

import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path

import pandas as pd

DB_POR_DEFECTO = Path(__file__).with_name("oes.db")

ESTADOS = ("Verificada", "Ejemplo didáctico", "Pendiente", "Descartada")

ESQUEMA = """
CREATE TABLE IF NOT EXISTS noticias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL CHECK (length(trim(titulo)) > 0),
    institucion TEXT NOT NULL CHECK (length(trim(institucion)) > 0),
    categoria TEXT NOT NULL,
    fuente TEXT NOT NULL,
    fecha TEXT NOT NULL CHECK (fecha GLOB '[0-9][0-9][0-9][0-9]-[01][0-9]-[0-3][0-9]'),
    url TEXT NOT NULL UNIQUE CHECK (url LIKE 'http://%' OR url LIKE 'https://%'),
    resumen TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'Ejemplo didáctico'
        CHECK (estado IN ('Verificada', 'Ejemplo didáctico', 'Pendiente', 'Descartada')),
    fecha_visible INTEGER NOT NULL DEFAULT 0 CHECK (fecha_visible IN (0, 1)),
    fecha_captura TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    verificado_por TEXT,
    fecha_verificacion TEXT
)
"""

CAMPOS = (
    "titulo",
    "institucion",
    "categoria",
    "fuente",
    "fecha",
    "url",
    "resumen",
    "estado",
    "fecha_visible",
    "verificado_por",
    "fecha_verificacion",
)


class NoticiaInvalida(ValueError):
    """La noticia no cumple las reglas de trazabilidad."""


def ruta_db() -> Path:
    """Ruta de la base; la variable OES_DB permite usar otra (por ejemplo, en las pruebas)."""
    return Path(os.environ.get("OES_DB", DB_POR_DEFECTO))


@contextmanager
def conectar(db: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Abre la base, crea la tabla si falta, confirma los cambios y SIEMPRE cierra la conexión."""
    con = sqlite3.connect(db or ruta_db())
    try:
        con.execute(ESQUEMA)
        yield con
        con.commit()
    finally:
        con.close()


def validar(noticia: dict) -> dict:
    """Comprueba la noticia antes de guardarla y devuelve una copia limpia."""
    limpia = {k: (v.strip() if isinstance(v, str) else v) for k, v in noticia.items()}
    for campo in ("titulo", "institucion", "categoria", "fuente", "fecha", "url", "resumen"):
        if not limpia.get(campo):
            raise NoticiaInvalida(f"Falta el campo obligatorio «{campo}».")
    try:
        date.fromisoformat(limpia["fecha"])
    except ValueError as error:
        raise NoticiaInvalida(f"Fecha inválida «{limpia['fecha']}»: use AAAA-MM-DD.") from error
    if not limpia["url"].startswith(("http://", "https://")):
        raise NoticiaInvalida("La URL debe empezar con http:// o https://.")
    estado = limpia.get("estado", "Ejemplo didáctico")
    if estado not in ESTADOS:
        raise NoticiaInvalida(f"Estado desconocido «{estado}».")
    if estado == "Verificada" and not limpia.get("verificado_por"):
        raise NoticiaInvalida("Una noticia verificada necesita «verificado_por».")
    return limpia


def insertar(con: sqlite3.Connection, noticias: list[dict]) -> int:
    """Inserta las noticias válidas; las URL repetidas se ignoran. Devuelve cuántas entraron."""
    antes = con.total_changes
    for noticia in noticias:
        limpia = validar(noticia)
        campos = [c for c in CAMPOS if c in limpia]
        con.execute(
            f"INSERT OR IGNORE INTO noticias ({', '.join(campos)}) VALUES ({', '.join('?' for _ in campos)})",
            [limpia[c] for c in campos],
        )
    con.commit()
    return con.total_changes - antes


def leer(con: sqlite3.Connection) -> pd.DataFrame:
    return pd.read_sql_query("SELECT * FROM noticias ORDER BY fecha DESC, id DESC", con)


def revisar(
    con: sqlite3.Connection, id_noticia: int, aprobar: bool, resumen: str = "", verificado_por: str = ""
) -> None:
    """Resuelve una noticia pendiente: la aprueba con un resumen propio o la descarta."""
    if aprobar:
        if len(resumen.strip()) < 20:
            raise NoticiaInvalida("Escriba un resumen propio de al menos 20 caracteres.")
        if not verificado_por.strip():
            raise NoticiaInvalida("Indique quién verificó la noticia.")
        con.execute(
            "UPDATE noticias SET estado = 'Verificada', resumen = ?, verificado_por = ?, "
            "fecha_verificacion = date('now', 'localtime') WHERE id = ? AND estado = 'Pendiente'",
            (resumen.strip(), verificado_por.strip(), id_noticia),
        )
    else:
        con.execute(
            "UPDATE noticias SET estado = 'Descartada', fecha_verificacion = date('now', 'localtime') "
            "WHERE id = ? AND estado = 'Pendiente'",
            (id_noticia,),
        )
    con.commit()
