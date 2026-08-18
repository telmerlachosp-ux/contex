from modelo_contable import crear_asiento

def generar_apertura_bancaria(monto_corriente, monto_fondo_fijo):
    total=round(monto_corriente+monto_fondo_fijo,2)
    return crear_asiento([
        {"codigo":"10410","cuenta":"Cuentas corrientes operativas","debe":monto_corriente,"haber":0},
        {"codigo":"10200","cuenta":"Fondos fijos","debe":monto_fondo_fijo,"haber":0},
        {"codigo":"10100","cuenta":"Caja","debe":0,"haber":total},
    ])
