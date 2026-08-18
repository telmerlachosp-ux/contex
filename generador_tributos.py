from modelo_contable import crear_asiento

def generar_tributo_municipal(monto):
    return crear_asiento([
        {"codigo":"64310","cuenta":"Impuesto predial / arbitrios municipales","debe":monto,"haber":0},
        {"codigo":"40615","cuenta":"Impuesto predial por pagar","debe":0,"haber":monto},
    ])

def generar_pago_tributo(monto, cuenta_efectivo="10200"):
    return crear_asiento([
        {"codigo":"40615","cuenta":"Impuesto predial por pagar","debe":monto,"haber":0},
        {"codigo":cuenta_efectivo,"cuenta":"Fondos fijos","debe":0,"haber":monto},
    ])
