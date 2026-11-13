# Paso 7: agrega noticias REALES verificadas manualmente el 12/11/2026.
# Para cada una se abrió el enlace directo y se comprobó que el titular y la fecha
# coinciden con la fuente. Los titulares se copian tal como figuran en la fuente;
# los resúmenes son de redacción propia. Fecha = fecha de publicación en la fuente.
import sqlite3
from pathlib import Path

DB = Path(__file__).with_name("oes.db")

verificadas = [
    ("Sunedu verifica condiciones de calidad en universidades públicas y privadas del país",
     "SUNEDU", "Ente regulador", "Agencia Andina (Editora Perú)", "2026-10-08",
     "https://andina.pe/agencia/noticia-sunedu-verifica-condiciones-calidad-universidades-publicas-y-privadas-del-pais-1095135.aspx",
     "La Sunedu ejecuta su Plan de Supervisión 2026 para comprobar que las universidades mantengan "
     "las seis Condiciones Básicas de Calidad, con énfasis en Puno, Arequipa, Moquegua y Tacna."),
    ("UNDC Y UNIVERSIDAD ANDINA DEL CUSCO SUSCRIBEN CONVENIO DE COOPERACIÓN INTERINSTITUCIONAL",
     "UNDC", "Universidad pública", "Portal institucional UNDC", "2026-10-23",
     "https://web.undc.edu.pe/undc-y-universidad-andina-del-cusco-suscriben-convenio-de-cooperacion-interinstitucional/",
     "La UNDC y la Universidad Andina del Cusco firmaron un convenio marco para colaborar en "
     "formación académica e investigación en beneficio de estudiantes y docentes."),
    ("EL CAMINO A LA UNDC COMIENZA HOY, CEPRE UNDC INCIO EL CICLO ORDINARIO 2026-II CON VACANTES DE INGRESO DIRECTO",
     "UNDC", "Universidad pública", "Portal institucional UNDC", "2026-10-23",
     "https://web.undc.edu.pe/el-camino-a-la-undc-comienza-hoy-cepre-undc-incio-el-ciclo-ordinario-2026-ii-con-vacantes-de-ingreso-directo/",
     "El centro preuniversitario de la UNDC inauguró su ciclo ordinario 2026-II, que otorga vacantes "
     "de ingreso directo, y mantiene abiertas las inscripciones."),
    ("Hay Festival Arequipa 2026: la PUCP llevó a Bryce a las calles y abrió debates sobre identidad e IA",
     "PUCP", "Universidad privada", "PuntoEdu PUCP", "2026-11-10",
     "https://puntoedu.pucp.edu.pe/vida-universitaria/institucional/hay-festival-arequipa-2026-la-pucp-debates-sobre-identidad-e-ia/",
     "La PUCP participó en el Hay Festival Arequipa 2026 con lecturas de Bryce y conversatorios sobre "
     "migración e inteligencia artificial."),
]

with sqlite3.connect(DB) as con:
    antes = con.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
    con.executemany("""INSERT OR IGNORE INTO noticias
        (titulo,institucion,categoria,fuente,fecha,url,resumen)
        VALUES (?,?,?,?,?,?,?)""", verificadas)
    despues = con.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]

print(f"Noticias antes: {antes} | después: {despues} | agregadas: {despues - antes}")
