"""Paso 4: crea la base y carga los 3 registros DEMOSTRATIVOS de la guía."""

from datos import conectar, insertar, ruta_db

EJEMPLOS = [
    {
        "titulo": "Ejemplo: convocatoria de becas",
        "institucion": "PRONABEC",
        "categoria": "Ente rector",
        "fuente": "Portal institucional (ejemplo)",
        "fecha": "2026-11-06",
        "url": "https://www.pronabec.gob.pe/",
        "resumen": "Registro didáctico: verificar nota original.",
    },
    {
        "titulo": "Ejemplo: actividad de investigación",
        "institucion": "UNMSM",
        "categoria": "Universidad pública",
        "fuente": "Portal institucional (ejemplo)",
        "fecha": "2026-11-06",
        "url": "https://www.unmsm.edu.pe/",
        "resumen": "Registro didáctico: verificar noticia original.",
    },
    {
        "titulo": "Ejemplo: programa académico",
        "institucion": "PUCP",
        "categoria": "Universidad privada",
        "fuente": "Portal institucional (ejemplo)",
        "fecha": "2026-11-05",
        "url": "https://www.pucp.edu.pe/",
        "resumen": "Registro didáctico: verificar noticia original.",
    },
]

if __name__ == "__main__":
    with conectar() as con:
        nuevas = insertar(con, [{**e, "estado": "Ejemplo didáctico"} for e in EJEMPLOS])
    print("Base creada:", ruta_db(), f"| registros nuevos: {nuevas}")
