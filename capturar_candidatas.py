"""Captura semiautomática: trae noticias candidatas desde las API públicas de los portales.

Las noticias entran como «Pendiente» y NO se muestran como información verificada hasta
que una persona las aprueba en la Bandeja de revisión del tablero (con resumen propio).
Solo se usan API públicas de WordPress (sin extraer HTML), con pocas solicitudes, un
User-Agent identificable y verificación de certificados activa.
"""

import html
import json
import re
import ssl
import unicodedata
import urllib.request

import truststore

from datos import conectar, insertar

FUENTES_API = [
    {
        "institucion": "UNDC",
        "categoria": "Universidad pública",
        "fuente": "Portal institucional UNDC",
        "api": "https://web.undc.edu.pe/wp-json/wp/v2/posts",
        "fecha_visible": 0,
    },
    {
        "institucion": "PUCP",
        "categoria": "Universidad privada",
        "fuente": "PuntoEdu PUCP",
        "api": "https://puntoedu.pucp.edu.pe/wp-json/wp/v2/posts",
        "fecha_visible": 1,
    },
]
POR_FUENTE = 5
AGENTE = "OES-academico/1.0 (practica universitaria UNDC; uso no comercial)"
CONTEXTO_TLS = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)  # almacén de certificados de Windows


def limpiar(texto: str) -> str:
    """Quita etiquetas HTML y convierte letras decorativas (p. ej. 𝐔𝐍𝐃𝐂) en texto normal (NFKC)."""
    plano = html.unescape(re.sub(r"<[^>]+>", " ", texto))
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", plano)).strip()


def candidatas(fuente: dict) -> list[dict]:
    url = f"{fuente['api']}?per_page={POR_FUENTE}&_fields=date,link,title"
    pedido = urllib.request.Request(url, headers={"User-Agent": AGENTE})
    with urllib.request.urlopen(pedido, timeout=20, context=CONTEXTO_TLS) as respuesta:
        entradas = json.load(respuesta)
    return [
        {
            "titulo": limpiar(e["title"]["rendered"]),
            "institucion": fuente["institucion"],
            "categoria": fuente["categoria"],
            "fuente": fuente["fuente"],
            "fecha": e["date"][:10],
            "url": e["link"],
            "resumen": "Pendiente de revisión: falta redactar el resumen propio.",
            "estado": "Pendiente",
            "fecha_visible": fuente["fecha_visible"],
        }
        for e in entradas
    ]


if __name__ == "__main__":
    with conectar() as con:
        for fuente in FUENTES_API:
            try:
                nuevas = insertar(con, candidatas(fuente))
                print(f"{fuente['fuente']}: {nuevas} candidatas nuevas en la bandeja")
            except (OSError, ValueError, KeyError) as error:
                print(f"{fuente['fuente']}: no se pudo consultar ({error})")
