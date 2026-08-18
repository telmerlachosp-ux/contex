from modelo_contable import crear_asiento

def generar_cobro(monto, tipo="FACTURA", cuenta_efectivo="10410"):
    if tipo.upper()=="LETRA":
        codigo, nombre="12300","Letras por cobrar"
    else:
        codigo, nombre="12120","Facturas emitidas en cartera"
    return crear_asiento([
        {"codigo":cuenta_efectivo,"cuenta":"Cuentas corrientes operativas","debe":monto,"haber":0},
        {"codigo":codigo,"cuenta":nombre,"debe":0,"haber":monto},
    ])
