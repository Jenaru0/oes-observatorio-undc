import pandas as pd

import analisis
import datos


def tabla(db):
    with datos.conectar() as con:
        return analisis.enriquecer(datos.leer(con))


def test_temas_ignoran_tildes_y_mayusculas():
    assert analisis.temas_de("CEPRE inició el ciclo con VACANTES", "") == ["Admisión y captación"]
    assert analisis.temas_de("Convenio de cooperación", "") == ["Alianzas y convenios"]
    assert analisis.temas_de("Texto sin claves", "") == [analisis.SIN_TEMA]


def test_trazabilidad_distingue_ejemplos_de_noticias_verificadas(db_completa):
    df = tabla(db_completa).set_index("institucion")
    assert set(df.loc[df["estado"] == "Ejemplo didáctico", "trazabilidad"]) == {0}
    assert df.loc["SUNEDU", "trazabilidad"] == 100
    assert set(df.loc["UNDC", "trazabilidad"]) == {80}  # la página no muestra la fecha


def test_trazabilidad_no_cuenta_revisor_vacio():
    fila = pd.Series(
        {
            "url": "https://x.pe/nota",
            "fecha_visible": 1,
            "estado": "Verificada",
            "verificado_por": float("nan"),
            "fuente": "Portal",
        }
    )
    assert analisis.trazabilidad(fila) == 70


def test_filtrar_por_categoria_texto_y_fecha(db_completa):
    df = tabla(db_completa)
    todas, estados = df["categoria"].unique(), ["Verificada", "Ejemplo didáctico"]
    assert len(analisis.filtrar(df, ["Universidad pública"], ["Ejemplo didáctico"])) == 1
    assert len(analisis.filtrar(df, todas, estados, busqueda="pucp")) == 2
    assert len(analisis.filtrar(df, todas, estados, busqueda="investigacion")) == 1  # sin tilde
    assert len(analisis.filtrar(df, todas, estados, desde="2026-11-01")) == 4


def test_alertas_y_radar(db_completa):
    df = tabla(db_completa)
    avisos = analisis.alertas(df)
    assert list(avisos["institucion"]) == ["SUNEDU"]  # «Plan de Supervisión»
    radar = analisis.radar(df)
    assert radar["noticias"].sum() >= (df["estado"] == "Verificada").sum()  # una noticia puede tener varios temas


def test_radar_solo_cuenta_noticias_verificadas(db_completa):
    radar = analisis.radar(tabla(db_completa))
    assert set(radar["institucion"]) == {"SUNEDU", "UNDC", "PUCP"}  # sin PRONABEC ni UNMSM de ejemplo
    assert analisis.SIN_TEMA not in set(radar["tema"])
