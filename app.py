"""Tablero del Observatorio de Educación Superior (prototipo académico)."""

from datetime import date

import altair as alt
import pandas as pd
import streamlit as st

import analisis
import datos

AZUL = "#2a78d6"  # tono único de las barras (paleta validada de la skill dataviz)
RAMPA = ["#cde2fb", "#104281"]  # rampa secuencial azul para el mapa de calor
GRILLA = "#e2e8f0"
ESTADOS_VISIBLES = ["Verificada", "Ejemplo didáctico"]
ICONO_ESTADO = {
    "Verificada": ":material/verified:",
    "Ejemplo didáctico": ":material/science:",
    "Pendiente": ":material/pending:",
    "Descartada": ":material/block:",
}
COLOR_ESTADO = {"Verificada": "green", "Ejemplo didáctico": "orange", "Pendiente": "blue", "Descartada": "gray"}

st.set_page_config(page_title="OES académico", page_icon=":material/school:", layout="wide")


# ----------------------------------------------------------------------------- datos
with datos.conectar() as con:
    base = analisis.enriquecer(datos.leer(con))

st.title("Observatorio de Educación Superior")
st.caption(
    "Prototipo académico de monitoreo institucional y regulatorio · UNDC · "
    "Inteligencia Artificial Aplicada al Marketing Digital · 2026-II"
)

if base.empty:
    st.warning("No hay noticias. Ejecute preparar_datos.py", icon=":material/database:")
    st.stop()


# ----------------------------------------------------------------------------- filtros
categorias = sorted(base["categoria"].unique())
fecha_min = pd.to_datetime(base["fecha"]).min().date()
fecha_max = max(pd.to_datetime(base["fecha"]).max().date(), date.today())


INICIALES = {"categorias": categorias, "estados": ESTADOS_VISIBLES, "rango": (fecha_min, fecha_max), "busqueda": ""}
for clave, valor in INICIALES.items():  # el estado de los filtros se inicializa una sola vez por sesión
    st.session_state.setdefault(clave, valor)
st.session_state.categorias = [c for c in st.session_state.categorias if c in categorias]


def restablecer():
    st.session_state.update(INICIALES)


with st.sidebar:
    st.header("Filtros", divider="gray")
    sel_categorias = st.multiselect("Categoría", categorias, key="categorias")
    sel_estados = st.pills(
        "Estado de verificación",
        ESTADOS_VISIBLES,
        selection_mode="multi",
        key="estados",
        help="Las pendientes y descartadas se gestionan en la Bandeja de revisión.",
    )
    rango = st.date_input(
        "Fecha de publicación", min_value=fecha_min, max_value=fecha_max, format="DD/MM/YYYY", key="rango"
    )
    busqueda = st.text_input("Buscar título o institución", key="busqueda", placeholder="Ej.: PUCP, convenio, Sunedu")
    st.button("Restablecer filtros", icon=":material/restart_alt:", on_click=restablecer, width="stretch")
    with st.expander("Palabras vigiladas (alertas)", icon=":material/notifications:"):
        vigiladas = st.text_input("Separadas por comas", ", ".join(analisis.ALERTAS_POR_DEFECTO))
    st.caption(
        f"Base actualizada al {pd.to_datetime(base['fecha_captura']).max():%d/%m/%Y} · {len(base)} registros en total"
    )

desde, hasta = (rango + (None,))[:2] if isinstance(rango, tuple) else (rango, None)
filtrado = analisis.filtrar(base, sel_categorias, sel_estados or [], desde=desde, hasta=hasta, busqueda=busqueda)


# ----------------------------------------------------------------------------- indicadores
verificadas = int((filtrado["estado"] == "Verificada").sum())
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Noticias", len(filtrado), border=True)
c2.metric("Instituciones", filtrado["institucion"].nunique(), border=True)
c3.metric("Categorías", filtrado["categoria"].nunique(), border=True)
c4.metric(
    "Verificadas",
    f"{verificadas} de {len(filtrado)}",
    border=True,
    help="Noticias revisadas por una persona contra la fuente original.",
)
c5.metric(
    "Trazabilidad media",
    f"{filtrado['trazabilidad'].mean():.0f} / 100" if len(filtrado) else "—",
    border=True,
    help="Promedio del índice de trazabilidad (ver pestaña Metodología).",
)

pendientes = base[base["estado"] == "Pendiente"]
tab_panorama, tab_noticias, tab_bandeja, tab_metodo = st.tabs(
    [
        ":material/insights: Panorama",
        ":material/article: Noticias",
        f":material/inbox: Bandeja de revisión ({len(pendientes)})",
        ":material/menu_book: Metodología",
    ]
)


def barras(df: pd.DataFrame, campo: str, titulo: str) -> alt.LayerChart:
    """Barras horizontales de un solo tono, ordenadas de mayor a menor, con su valor al final."""
    conteo = df[campo].value_counts().rename_axis(campo).reset_index(name="noticias")
    eje_y = alt.Y(f"{campo}:N", sort="-x", title=None, axis=alt.Axis(labelLimit=180))
    base_chart = alt.Chart(conteo, title=titulo).encode(
        y=eje_y,
        x=alt.X("noticias:Q", title=None, axis=alt.Axis(tickMinStep=1, gridColor=GRILLA)),
        tooltip=[alt.Tooltip(f"{campo}:N", title=titulo), alt.Tooltip("noticias:Q", title="Noticias")],
    )
    marcas = base_chart.mark_bar(color=AZUL, size=20, cornerRadiusEnd=4)
    etiquetas = base_chart.mark_text(align="left", dx=6, color="#0f172a").encode(text="noticias:Q")
    return (marcas + etiquetas).properties(height=48 * len(conteo) + 20)


# ----------------------------------------------------------------------------- panorama
with tab_panorama:
    avisos = analisis.alertas(filtrado, [p for p in vigiladas.split(",")])
    if len(avisos):
        with st.container(border=True):
            plural = "alerta" if len(avisos) == 1 else "alertas"
            st.markdown(f":material/notifications_active: **{len(avisos)} {plural} por palabras vigiladas**")
            for _, fila in avisos.iterrows():
                st.markdown(f"- {fila['fecha']} · **{fila['institucion']}** · [{fila['titulo']}]({fila['url']})")

    if filtrado.empty:
        st.info("No hay resultados con esos filtros", icon=":material/filter_alt_off:")
        st.caption("Quite algún filtro o use «Restablecer filtros» en la barra lateral.")
    else:
        g1, g2 = st.columns(2)
        g1.altair_chart(barras(filtrado, "categoria", "Noticias por categoría"), width="stretch")
        g2.altair_chart(barras(filtrado, "institucion", "Noticias por institución"), width="stretch")

        st.subheader("Radar de temas para marketing educativo")
        st.caption(
            "Qué comunica cada institución, según palabras clave del título y del resumen. "
            "Describe actividad comunicacional, no calidad académica."
        )
        conteo = analisis.radar(filtrado)
        orden_temas = [*analisis.TEMAS, analisis.SIN_TEMA]
        celdas = alt.Chart(conteo).encode(
            y=alt.Y(
                "tema:N",
                sort=orden_temas,
                scale=alt.Scale(domain=orden_temas),
                title=None,
                axis=alt.Axis(labelLimit=220, labelFontSize=13),
            ),
            x=alt.X("institucion:N", title=None, axis=alt.Axis(orient="top", labelAngle=0, labelFontSize=13)),
            tooltip=[
                alt.Tooltip("institucion:N", title="Institución"),
                alt.Tooltip("tema:N", title="Tema"),
                alt.Tooltip("noticias:Q", title="Noticias"),
            ],
        )
        tope = max(2, int(conteo["noticias"].max()))
        mapa = celdas.mark_rect(cornerRadius=4, stroke="white", strokeWidth=2, opacity=1).encode(
            color=alt.Color("noticias:Q", legend=None, scale=alt.Scale(domain=[0, tope], range=RAMPA))
        )
        numeros = celdas.mark_text(fontSize=14, fontWeight="bold").encode(  # texto claro solo sobre celdas oscuras
            text="noticias:Q",
            color=alt.condition(alt.datum.noticias >= tope * 0.6, alt.value("white"), alt.value("#0f172a")),
        )
        st.altair_chart((mapa + numeros).properties(height=44 * len(orden_temas)), width="stretch")


# ----------------------------------------------------------------------------- noticias
with tab_noticias:
    if filtrado.empty:
        st.info("No hay resultados con esos filtros", icon=":material/filter_alt_off:")
    tabla = filtrado.assign(fecha=pd.to_datetime(filtrado["fecha"]))
    evento = st.dataframe(
        tabla[["fecha", "institucion", "titulo", "estado", "trazabilidad", "url", "temas", "categoria"]],
        hide_index=True,
        width="stretch",
        on_select="rerun",
        selection_mode="single-row",
        key="tabla",
        column_config={
            "fecha": st.column_config.DateColumn("Fecha", format="DD/MM/YYYY"),
            "institucion": "Institución",
            "categoria": "Categoría",
            "titulo": st.column_config.TextColumn("Título", width="medium"),
            "temas": st.column_config.ListColumn("Temas"),
            "estado": "Estado",
            "trazabilidad": st.column_config.ProgressColumn("Trazabilidad", min_value=0, max_value=100, format="%d"),
            "url": st.column_config.LinkColumn("Fuente", display_text="Abrir nota"),
        },
    )
    st.caption("Seleccione una fila para ver su ficha completa.")

    if evento.selection.rows:
        fila = tabla.iloc[evento.selection.rows[0]]
        with st.container(border=True):
            st.subheader(fila["titulo"])
            b1, b2, b3 = st.columns([1, 1, 3])
            with b1:
                st.badge(fila["estado"], icon=ICONO_ESTADO[fila["estado"]], color=COLOR_ESTADO[fila["estado"]])
            with b2:
                st.badge(fila["categoria"], icon=":material/category:", color="gray")
            st.write(fila["resumen"])
            revisor = fila["verificado_por"] if analisis.tiene_texto(fila["verificado_por"]) else "—"
            st.caption(
                f"{fila['institucion']} · {fila['fuente']} · publicada el {fila['fecha']:%d/%m/%Y} · "
                f"verificada por: {revisor}"
            )
            st.markdown(f"**Trazabilidad: {fila['trazabilidad']} / 100**")
            for criterio, ok in analisis.criterios_cumplidos(fila).items():
                marca = ":green[:material/check_circle: Cumple]" if ok else ":gray[:material/cancel: No cumple]"
                st.markdown(f"{marca} · {criterio} ({analisis.CRITERIOS[criterio]} puntos)")
            st.link_button("Abrir nota original", fila["url"], icon=":material/open_in_new:")

    exportable = filtrado.assign(temas=filtrado["temas"].str.join("; "))  # texto plano, legible en Excel
    st.download_button(
        "Exportar CSV",
        data=exportable.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"oes_resultados_{date.today():%Y%m%d}.csv",
        mime="text/csv",
        icon=":material/download:",
    )


# ----------------------------------------------------------------------------- bandeja
with tab_bandeja:
    st.caption(
        "Noticias traídas por capturar_candidatas.py desde API públicas. No cuentan en los "
        "indicadores hasta que una persona las aprueba con un resumen propio."
    )
    if pendientes.empty:
        st.success("No hay noticias pendientes de revisión.", icon=":material/task_alt:")
    for _, fila in pendientes.iterrows():
        with st.form(f"revision_{fila['id']}", border=True):
            st.markdown(f"**{fila['titulo']}**")
            st.caption(f"{fila['institucion']} · {fila['fuente']} · {fila['fecha']} · [Abrir nota]({fila['url']})")
            resumen = st.text_area("Resumen propio", placeholder="Redacte con sus palabras lo esencial de la nota")
            revisor = st.text_input("Verificado por")
            confirmo = st.checkbox("Abrí el enlace y el titular y la fecha coinciden con la fuente")
            a1, a2, _ = st.columns([1, 1, 4])
            aprobar = a1.form_submit_button("Aprobar", icon=":material/check:", type="primary")
            descartar = a2.form_submit_button("Descartar", icon=":material/close:")
        if aprobar or descartar:
            try:
                if aprobar and not confirmo:
                    raise datos.NoticiaInvalida("Confirme que revisó el enlace antes de aprobar.")
                with datos.conectar() as con:
                    datos.revisar(con, int(fila["id"]), aprobar, resumen, revisor)
                st.rerun()
            except datos.NoticiaInvalida as error:
                st.error(str(error), icon=":material/error:")


# ----------------------------------------------------------------------------- metodología
with tab_metodo:
    st.markdown("""
**Flujo:** fuente oficial → captura (manual o API pública) → validación → base SQLite →
revisión humana → tablero → exportación y decisiones.

**Validación automática:** campos obligatorios, fecha AAAA-MM-DD, URL http(s) y única
(no se duplican noticias), estado permitido, y toda noticia verificada indica quién la verificó.
""")
    m1, m2 = st.columns(2)
    with m1:
        st.markdown("**Índice de trazabilidad (0-100)**")
        st.dataframe(
            pd.DataFrame(analisis.CRITERIOS.items(), columns=["Criterio", "Puntos"]), hide_index=True, width="stretch"
        )
    with m2:
        st.markdown("**Temas y palabras clave**")
        st.dataframe(
            pd.DataFrame([(t, ", ".join(c)) for t, c in analisis.TEMAS.items()], columns=["Tema", "Palabras clave"]),
            hide_index=True,
            width="stretch",
        )
    st.markdown("""
**Límites:** los conteos describen lo que se registró, no la calidad de una universidad;
la muestra es pequeña; gob.pe (MINEDU, SUNEDU) bloqueó el acceso automatizado; algunas páginas
no muestran la fecha y se usa la fecha de publicación del portal. Los 3 registros de ejemplo de
la guía deben retirarse antes de cualquier uso institucional.
""")

st.divider()
st.caption(
    "Prototipo académico con datos verificados manualmente. Confirme siempre en la fuente "
    "original antes de un uso institucional. No reproduce el código ni la identidad del OES comercial."
)
