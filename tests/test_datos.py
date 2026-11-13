import pytest

import datos
import preparar_datos

NOTICIA = {
    "titulo": "Título",
    "institucion": "UNDC",
    "categoria": "Universidad pública",
    "fuente": "Portal institucional UNDC",
    "fecha": "2026-11-12",
    "url": "https://web.undc.edu.pe/nota/",
    "resumen": "Resumen propio de la nota.",
}


def contar(con):
    return con.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]


def test_p1_carga_doble_no_duplica(db):
    with datos.conectar() as con:
        repetidas = datos.insertar(con, [{**e, "estado": "Ejemplo didáctico"} for e in preparar_datos.EJEMPLOS])
        assert repetidas == 0
        assert contar(con) == 3


@pytest.mark.parametrize(
    "cambio, mensaje",
    [
        ({"titulo": "  "}, "titulo"),
        ({"fecha": "12/11/2026"}, "Fecha inválida"),
        ({"fecha": "2026-13-40"}, "Fecha inválida"),
        ({"url": "web.undc.edu.pe/nota"}, "URL"),
        ({"estado": "Aprobada"}, "Estado desconocido"),
        ({"estado": "Verificada"}, "verificado_por"),
    ],
)
def test_rechaza_noticias_invalidas(db, cambio, mensaje):
    with datos.conectar() as con, pytest.raises(datos.NoticiaInvalida, match=mensaje):
        datos.insertar(con, [{**NOTICIA, **cambio}])


def test_la_base_tambien_rechaza_fecha_mal_escrita(db):
    """Defensa en profundidad: aunque se salte la validación en Python, la base la rechaza."""
    with datos.conectar() as con, pytest.raises(Exception, match="CHECK"):
        con.execute(
            "INSERT INTO noticias (titulo, institucion, categoria, fuente, fecha, url, resumen) "
            "VALUES ('t', 'i', 'c', 'f', '12/11/2026', 'https://x.pe/a', 'r')"
        )


def test_revision_aprueba_con_resumen_y_revisor(db):
    with datos.conectar() as con:
        datos.insertar(con, [{**NOTICIA, "estado": "Pendiente"}])
        id_nota = con.execute("SELECT id FROM noticias WHERE estado = 'Pendiente'").fetchone()[0]
        with pytest.raises(datos.NoticiaInvalida, match="resumen"):
            datos.revisar(con, id_nota, aprobar=True, resumen="corto", verificado_por="Ana")
        datos.revisar(con, id_nota, aprobar=True, resumen="Resumen propio suficientemente largo.", verificado_por="Ana")
        estado, revisor = con.execute("SELECT estado, verificado_por FROM noticias WHERE id = ?", (id_nota,)).fetchone()
    assert (estado, revisor) == ("Verificada", "Ana")


def test_revision_descarta(db):
    with datos.conectar() as con:
        datos.insertar(con, [{**NOTICIA, "estado": "Pendiente"}])
        id_nota = con.execute("SELECT id FROM noticias WHERE estado = 'Pendiente'").fetchone()[0]
        datos.revisar(con, id_nota, aprobar=False)
        assert con.execute("SELECT estado FROM noticias WHERE id = ?", (id_nota,)).fetchone()[0] == "Descartada"


def test_conexion_siempre_se_cierra(db):
    """En Windows un archivo abierto no se puede borrar: si se borra, la conexión quedó cerrada."""
    with datos.conectar() as con:
        con.execute("SELECT 1")
    db.unlink()
    assert not db.exists()
