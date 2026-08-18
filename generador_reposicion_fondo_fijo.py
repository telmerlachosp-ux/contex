from modelo_contable import crear_asiento

def generar_reposicion_fondo_fijo(monto, cuenta_banco="10410"):
    return crear_asiento([
        {"codigo":"10200","cuenta":"Fondos fijos","debe":monto,"haber":0},
        {"codigo":cuenta_banco,"cuenta":"Cuentas corrientes operativas","debe":0,"haber":monto},
    ])
