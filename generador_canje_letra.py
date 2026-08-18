from modelo_contable import crear_asiento

def generar_canje_letra(monto):
    return crear_asiento([
        {"codigo":"12300","cuenta":"Letras por cobrar","debe":monto,"haber":0},
        {"codigo":"12120","cuenta":"Facturas emitidas en cartera","debe":0,"haber":monto},
    ])
