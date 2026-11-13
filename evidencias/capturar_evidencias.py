"""Genera las evidencias de las pruebas manejando el tablero en un navegador real (Edge).

Requiere el tablero corriendo:  streamlit run app.py --server.headless true
Uso:  python evidencias/capturar_evidencias.py inicial   (P0, P2, P3, P4, P5; solo los 3 ejemplos)
      python evidencias/capturar_evidencias.py final     (P6, después de agregar_noticias.py)
      python evidencias/capturar_evidencias.py bandeja   (novedad, después de capturar_candidatas.py)
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://localhost:8501"
CARPETA = Path(__file__).parent
FILA_0, ALTO_FILA = 53, 35  # centro de la primera fila de la tabla y alto de cada fila (px)


def esperar(page):
    page.wait_for_timeout(1200)
    page.wait_for_selector('[data-testid="stStatusWidget"]', state="detached", timeout=15000)
    page.wait_for_timeout(1500)


def metricas(page):
    valores = page.locator('[data-testid="stMetricValue"]').all_inner_texts()
    return dict(zip(["Noticias", "Instituciones", "Categorías", "Verificadas", "Trazabilidad"], valores, strict=False))


def pestana(page, nombre):
    page.get_by_role("tab", name=nombre).click()
    esperar(page)


def buscar(page, texto):
    caja = page.get_by_label("Buscar título o institución")
    caja.fill(texto)
    caja.press("Enter")
    esperar(page)


def captura(page, nombre):
    page.evaluate("document.querySelector('[data-testid=\"stMain\"]')?.scrollTo(0, 0)")
    page.wait_for_timeout(300)
    page.screenshot(path=CARPETA / nombre)
    print(f"{nombre}: {metricas(page)}")


def exportar(page, destino):
    with page.expect_download() as descarga:
        page.get_by_role("button", name="Exportar CSV").click()
    descarga.value.save_as(CARPETA / destino)
    print("CSV guardado:", destino)


modo = sys.argv[1] if len(sys.argv) > 1 else "inicial"
with sync_playwright() as p:
    navegador = p.chromium.launch(channel="msedge")  # usa el Edge instalado en Windows
    page = navegador.new_page(viewport={"width": 1440, "height": 1250}, accept_downloads=True)
    page.goto(URL)
    page.wait_for_selector('[data-testid="stMetricValue"]', timeout=30000)
    esperar(page)

    if modo == "inicial":
        captura(page, "P0_tablero_inicial.png")

        for categoria in ("Ente rector", "Universidad privada"):  # P2: solo «Universidad pública»
            page.locator(f'[data-testid="stMultiSelect"] button[aria-label="Remove {categoria}"]').last.click()
            esperar(page)
        pestana(page, "Noticias")
        captura(page, "P2_filtro_universidad_publica.png")

        page.get_by_role("button", name="Restablecer filtros").click()
        esperar(page)
        buscar(page, "PUCP")  # P3
        captura(page, "P3_busqueda_pucp.png")
        exportar(page, "P5_oes_resultados_PUCP.csv")  # P5 con el filtro activo

        buscar(page, "zzz-termino-inexistente")  # P4
        captura(page, "P4_busqueda_inexistente.png")
        aviso = page.get_by_text("No hay resultados con esos filtros").filter(visible=True)
        print("Aviso visible:", aviso.count() > 0)

        buscar(page, "")
        exportar(page, "P5_oes_resultados_todos.csv")

    elif modo == "final":
        page.set_viewport_size({"width": 1440, "height": 1500})
        captura(page, "P6_panorama_con_noticias_reales.png")
        pestana(page, "Noticias")
        page.locator('[data-testid="stDataFrame"]').first.click(position={"x": 15, "y": FILA_0 + 6 * ALTO_FILA})
        esperar(page)
        captura(page, "P6_noticias_y_ficha_sunedu.png")

    else:  # bandeja
        pestana(page, "Bandeja de revisión")
        captura(page, "N1_bandeja_pendientes.png")
        form = page.locator('[data-testid="stForm"]', has_text="YANAPAY").first
        form.get_by_label("Resumen propio").fill(
            "La Dirección de Responsabilidad Social Universitaria de la UNDC dio la bienvenida, el 21 de "
            "octubre, a los voluntarios del programa YANAPAY 2026-II."
        )
        form.get_by_label("Verificado por").fill("Jhonatan Napanga Ruiz")
        form.get_by_text("Abrí el enlace y el titular y la fecha coinciden con la fuente").click()
        form.screenshot(path=CARPETA / "N2_formulario_aprobacion.png")
        form.get_by_role("button", name="Aprobar").click()
        esperar(page)
        pestana(page, "Bandeja de revisión")
        captura(page, "N3_bandeja_tras_aprobar.png")
        pestana(page, "Panorama")
        captura(page, "N4_panorama_final.png")

    navegador.close()
