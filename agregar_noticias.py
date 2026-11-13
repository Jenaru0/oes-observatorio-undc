"""Paso 7: agrega noticias REALES verificadas manualmente el 12/11/2026.

Para cada una se abrió el enlace directo y se comprobó que el titular y la fecha coinciden
con la fuente. Los titulares se copian tal como figuran (incluida la errata «INCIO» del
original); los resúmenes son de redacción propia. Fecha = fecha de publicación en la fuente.
"""

from datos import conectar, insertar

VERIFICACION = {"estado": "Verificada", "verificado_por": "Jhonatan Napanga Ruiz", "fecha_verificacion": "2026-11-12"}

VERIFICADAS = [
    {
        "titulo": "Sunedu verifica condiciones de calidad en universidades públicas y privadas del país",
        "institucion": "SUNEDU",
        "categoria": "Ente regulador",
        "fuente": "Agencia Andina (Editora Perú)",
        "fecha": "2026-10-08",
        "fecha_visible": 1,
        "url": "https://andina.pe/agencia/noticia-sunedu-verifica-condiciones-calidad-universidades-"
        "publicas-y-privadas-del-pais-1095135.aspx",
        "resumen": "La Sunedu ejecuta su Plan de Supervisión 2026 para comprobar que las universidades "
        "mantengan las seis Condiciones Básicas de Calidad, con énfasis en Puno, Arequipa, "
        "Moquegua y Tacna.",
    },
    {
        "titulo": "UNDC Y UNIVERSIDAD ANDINA DEL CUSCO SUSCRIBEN CONVENIO DE COOPERACIÓN INTERINSTITUCIONAL",
        "institucion": "UNDC",
        "categoria": "Universidad pública",
        "fuente": "Portal institucional UNDC",
        "fecha": "2026-10-23",
        "fecha_visible": 0,
        "url": "https://web.undc.edu.pe/undc-y-universidad-andina-del-cusco-suscriben-convenio-de-"
        "cooperacion-interinstitucional/",
        "resumen": "La UNDC y la Universidad Andina del Cusco firmaron un convenio marco para colaborar "
        "en formación académica e investigación en beneficio de estudiantes y docentes.",
    },
    {
        "titulo": "EL CAMINO A LA UNDC COMIENZA HOY, CEPRE UNDC INCIO EL CICLO ORDINARIO 2026-II CON "
        "VACANTES DE INGRESO DIRECTO",
        "institucion": "UNDC",
        "categoria": "Universidad pública",
        "fuente": "Portal institucional UNDC",
        "fecha": "2026-10-23",
        "fecha_visible": 0,
        "url": "https://web.undc.edu.pe/el-camino-a-la-undc-comienza-hoy-cepre-undc-incio-el-ciclo-"
        "ordinario-2026-ii-con-vacantes-de-ingreso-directo/",
        "resumen": "El centro preuniversitario de la UNDC inauguró su ciclo ordinario 2026-II, que otorga "
        "vacantes de ingreso directo, y mantiene abiertas las inscripciones.",
    },
    {
        "titulo": "Hay Festival Arequipa 2026: la PUCP llevó a Bryce a las calles y abrió debates sobre identidad e IA",
        "institucion": "PUCP",
        "categoria": "Universidad privada",
        "fuente": "PuntoEdu PUCP",
        "fecha": "2026-11-10",
        "fecha_visible": 1,
        "url": "https://puntoedu.pucp.edu.pe/vida-universitaria/institucional/hay-festival-arequipa-2026-"
        "la-pucp-debates-sobre-identidad-e-ia/",
        "resumen": "La PUCP participó en el Hay Festival Arequipa 2026 con lecturas de Bryce y "
        "conversatorios sobre migración e inteligencia artificial.",
    },
]

if __name__ == "__main__":
    with conectar() as con:
        antes = con.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
        insertar(con, [{**n, **VERIFICACION} for n in VERIFICADAS])
        despues = con.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
    print(f"Noticias antes: {antes} | después: {despues} | agregadas: {despues - antes}")
