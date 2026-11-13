"""Análisis local y explicable: temas por palabras clave, alertas e índice de trazabilidad."""

import re
import unicodedata
from urllib.parse import urlparse

import pandas as pd

# Temas de interés para el marketing educativo. Las reglas son palabras clave visibles
# (no un modelo opaco), para que cualquiera pueda revisar por qué se asignó un tema.
TEMAS = {
    "Admisión y captación": (
        "admision",
        "cepre",
        "preuniversitario",
        "ingreso directo",
        "vacantes",
        "postulante",
        "matricula",
    ),
    "Alianzas y convenios": ("convenio", "alianza", "cooperacion", "suscriben", "acuerdo"),
    "Calidad y regulación": (
        "sunedu",
        "licenciamiento",
        "supervision",
        "condiciones basicas",
        "calidad",
        "acreditacion",
        "minedu",
        "resolucion",
    ),
    "Investigación e innovación": (
        "investigacion",
        "ciencia",
        "innovacion",
        "concytec",
        "tecnologic",
        "inteligencia artificial",
    ),
    "Imagen y eventos": (
        "festival",
        "ceremonia",
        "honoris causa",
        "aniversario",
        "feria",
        "congreso",
        "premio",
        "reconocimiento",
    ),
    "Becas y bienestar": ("beca", "pronabec", "bienestar", "voluntari", "responsabilidad social"),
}
SIN_TEMA = "Sin tema"

# Palabras que disparan una alerta para el equipo de marketing (riesgo regulatorio).
ALERTAS_POR_DEFECTO = ("licenciamiento", "supervision", "sancion", "cierre", "cese")

# Criterios del índice de trazabilidad (suman 100).
CRITERIOS = {
    "URL directa a la nota": 30,
    "Fecha visible en la fuente": 20,
    "Verificada por una persona": 30,
    "Fuente institucional identificada": 20,
}


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para que «Admisión» y «admision» coincidan."""
    sin_tildes = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode()
    return sin_tildes.lower()


def menciona(texto: str, claves) -> bool:
    """True si alguna clave aparece al inicio de una palabra («supervision» sí, «acceso» no es «cese»)."""
    claves = [re.escape(normalizar(c).strip()) for c in claves if c.strip()]
    return bool(claves) and re.search(r"\b(?:" + "|".join(claves) + ")", normalizar(texto)) is not None


def temas_de(titulo: str, resumen: str) -> list[str]:
    texto = f"{titulo} {resumen}"
    encontrados = [tema for tema, claves in TEMAS.items() if menciona(texto, claves)]
    return encontrados or [SIN_TEMA]


def tiene_texto(valor) -> bool:
    """True solo para textos no vacíos (None y NaN de pandas cuentan como vacíos)."""
    return isinstance(valor, str) and bool(valor.strip())


def criterios_cumplidos(fila: pd.Series) -> dict[str, bool]:
    ruta = urlparse(fila["url"]).path
    return {
        "URL directa a la nota": ruta not in ("", "/"),
        "Fecha visible en la fuente": bool(fila["fecha_visible"]),
        "Verificada por una persona": fila["estado"] == "Verificada" and tiene_texto(fila["verificado_por"]),
        "Fuente institucional identificada": "ejemplo" not in normalizar(fila["fuente"]),
    }


def trazabilidad(fila: pd.Series) -> int:
    return sum(CRITERIOS[c] for c, ok in criterios_cumplidos(fila).items() if ok)


def enriquecer(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega las columnas calculadas: temas y trazabilidad."""
    df = df.copy()
    df["temas"] = [temas_de(t, r) for t, r in zip(df["titulo"], df["resumen"], strict=True)]
    df["trazabilidad"] = df.apply(trazabilidad, axis=1) if not df.empty else pd.Series(dtype=int)
    return df


def alertas(df: pd.DataFrame, palabras=ALERTAS_POR_DEFECTO) -> pd.DataFrame:
    """Noticias cuyo título o resumen contiene alguna palabra vigilada."""
    if df.empty:
        return df
    texto = df["titulo"] + " " + df["resumen"]
    return df[texto.map(lambda t: menciona(t, palabras))]


def filtrar(df: pd.DataFrame, categorias, estados, *, desde=None, hasta=None, busqueda="") -> pd.DataFrame:
    """Aplica los filtros del tablero. La búsqueda ignora mayúsculas y tildes."""
    mascara = df["categoria"].isin(categorias) & df["estado"].isin(estados)
    fechas = pd.to_datetime(df["fecha"])
    if desde is not None:
        mascara &= fechas >= pd.Timestamp(desde)
    if hasta is not None:
        mascara &= fechas <= pd.Timestamp(hasta)
    patron = normalizar(busqueda.strip())
    if patron:
        texto = (df["titulo"] + " " + df["institucion"]).map(normalizar)
        mascara &= texto.str.contains(patron, regex=False)
    return df[mascara]


def radar(df: pd.DataFrame) -> pd.DataFrame:
    """Conteo institución × tema de las noticias VERIFICADAS (los ejemplos no representan a nadie)."""
    df = df[df["estado"] == "Verificada"]
    if df.empty:
        return pd.DataFrame(columns=["institucion", "tema", "noticias"])
    largo = df[["institucion", "temas"]].explode("temas").rename(columns={"temas": "tema"})
    return largo.groupby(["institucion", "tema"]).size().reset_index(name="noticias")
