from modelo_contable import crear_asiento

def generar_honorarios(monto, igv=0):
    total=round(monto+igv,2)
    cuentas=[{"codigo":"63230","cuenta":"Asesoría y consultoría - Auditoría y contable","debe":monto,"haber":0}]
    if igv:
        cuentas.append({"codigo":"40111","cuenta":"IGV - Cuenta propia","debe":igv,"haber":0})
    cuentas.append({"codigo":"42400","cuenta":"Honorarios por pagar","debe":0,"haber":total})
    return crear_asiento(cuentas)

def generar_pago_honorarios(monto, cuenta_efectivo="10200"):
    return crear_asiento([
        {"codigo":"42400","cuenta":"Honorarios por pagar","debe":monto,"haber":0},
        {"codigo":cuenta_efectivo,"cuenta":"Fondos fijos","debe":0,"haber":monto},
    ])
