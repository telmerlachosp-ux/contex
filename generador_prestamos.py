from modelo_contable import crear_asiento

def generar_prestamo(monto, cuenta_banco="10410"):
    return crear_asiento([
        {"codigo":cuenta_banco,"cuenta":"Cuentas corrientes operativas","debe":monto,"haber":0},
        {"codigo":"45110","cuenta":"Préstamos de instituciones financieras","debe":0,"haber":monto},
    ])

def generar_prestamo_desde_enunciado(monto, cuenta_banco="10410"):
    return generar_prestamo(monto, cuenta_banco)

def generar_pago_prestamo(capital, intereses, cuenta_banco="10410"):
    total=round(capital+intereses,2)
    return crear_asiento([
        {"codigo":"45110","cuenta":"Préstamos de instituciones financieras","debe":capital,"haber":0},
        {"codigo":"67300","cuenta":"Gastos financieros - intereses","debe":intereses,"haber":0},
        {"codigo":cuenta_banco,"cuenta":"Cuentas corrientes operativas","debe":0,"haber":total},
    ])
