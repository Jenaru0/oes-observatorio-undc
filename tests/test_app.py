"""Pruebas del tablero completo con el simulador oficial de Streamlit (AppTest)."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

import datos

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def abrir():
    at = AppTest.from_file(APP, default_timeout=30)
    at.run()
    assert not at.exception
    return at


def indicadores(at):
    return {m.label: m.value for m in at.metric}


def test_p0_tablero_inicial_muestra_3_3_3(db):
    ind = indicadores(abrir())
    assert (ind["Noticias"], ind["Instituciones"], ind["Categorías"]) == ("3", "3", "3")


def test_p2_filtro_universidad_publica(db):
    at = abrir()
    at.multiselect(key="categorias").set_value(["Universidad pública"]).run()
    assert indicadores(at)["Noticias"] == "1"
    assert list(at.dataframe[0].value["institucion"]) == ["UNMSM"]


def test_p3_busqueda_pucp(db):
    at = abrir()
    at.text_input(key="busqueda").input("PUCP").run()
    assert indicadores(at)["Noticias"] == "1"


def test_p4_busqueda_inexistente_sin_error(db):
    at = abrir()
    at.text_input(key="busqueda").input("zzz-termino-inexistente").run()
    assert not at.exception
    assert indicadores(at)["Noticias"] == "0"
    assert any("No hay resultados" in i.value for i in at.info)


def test_p6_noticias_reales_aumentan_el_contador(db_completa):
    ind = indicadores(abrir())
    assert (ind["Noticias"], ind["Instituciones"], ind["Categorías"]) == ("7", "5", "4")
    assert ind["Verificadas"] == "4 de 7"


def test_bandeja_pendiente_no_cuenta_hasta_aprobarse(db):
    with datos.conectar() as con:
        datos.insertar(
            con,
            [
                {
                    "titulo": "Nota candidata",
                    "institucion": "UNDC",
                    "categoria": "Universidad pública",
                    "fuente": "Portal institucional UNDC",
                    "fecha": "2026-11-12",
                    "url": "https://web.undc.edu.pe/candidata/",
                    "resumen": "Pendiente",
                    "estado": "Pendiente",
                }
            ],
        )
    at = abrir()
    assert indicadores(at)["Noticias"] == "3"
    assert "Bandeja de revisión (1)" in at.tabs[2].label


def test_restablecer_filtros_devuelve_los_valores_iniciales(db):
    at = abrir()
    at.multiselect(key="categorias").set_value(["Universidad pública"]).run()
    at.text_input(key="busqueda").input("PUCP").run()
    assert indicadores(at)["Noticias"] == "0"
    at.button[0].click().run()
    assert indicadores(at)["Noticias"] == "3"
    assert at.text_input(key="busqueda").value == ""
