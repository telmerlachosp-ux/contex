from modelo_contable import crear_asiento

def generar_pago(monto, tipo="FACTURA", cuenta_efectivo="10410"):
    tipo=tipo.upper()
    if tipo=="HONORARIOS":
        codigo,nombre="42400","Honorarios por pagar"
    elif tipo=="TRIBUTOS":
        codigo,nombre="40615","Impuesto predial por pagar"
    else:
        codigo,nombre="42120","Facturas emitidas por pagar"
    return crear_asiento([
        {"codigo":codigo,"cuenta":nombre,"debe":monto,"haber":0},
        {"codigo":cuenta_efectivo,"cuenta":"Cuentas corrientes operativas","debe":0,"haber":monto},
    ])
