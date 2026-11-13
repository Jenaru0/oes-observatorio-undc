import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import agregar_noticias  # noqa: E402
import datos  # noqa: E402
import preparar_datos  # noqa: E402


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Base temporal con los 3 ejemplos de la guía (no toca oes.db)."""
    ruta = tmp_path / "prueba.db"
    monkeypatch.setenv("OES_DB", str(ruta))
    with datos.conectar() as con:
        datos.insertar(con, [{**e, "estado": "Ejemplo didáctico"} for e in preparar_datos.EJEMPLOS])
    return ruta


@pytest.fixture
def db_completa(db):
    """Base temporal con los ejemplos y las 4 noticias reales verificadas."""
    with datos.conectar() as con:
        datos.insertar(con, [{**n, **agregar_noticias.VERIFICACION} for n in agregar_noticias.VERIFICADAS])
    return db
