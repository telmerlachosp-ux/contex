from modelo_contable import crear_asiento

def generar_compra_terreno(monto, cuenta_efectivo="10410"):
    return crear_asiento([
        {"codigo":"33110","cuenta":"Terrenos","debe":monto,"haber":0},
        {"codigo":cuenta_efectivo,"cuenta":"Cuentas corrientes operativas","debe":0,"haber":monto},
    ])
