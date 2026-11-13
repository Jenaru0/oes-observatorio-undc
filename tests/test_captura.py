import capturar_candidatas


def test_limpiar_quita_html_y_letras_decorativas():
    titulo = "<strong>𝐔𝐍𝐃𝐂 participa</strong> en &laquo;encuentro&raquo;"
    assert capturar_candidatas.limpiar(titulo) == "UNDC participa en «encuentro»"
