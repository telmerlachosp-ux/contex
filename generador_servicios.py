from modelo_contable import crear_asiento

SERVICIOS={
    "AGUA":("63630","Agua"),
    "ENERGIA":("63610","Energía eléctrica"),
    "ENERGÍA":("63610","Energía eléctrica"),
    "ELECTRICIDAD":("63610","Energía eléctrica"),
    "INTERNET":("63650","Internet"),
}

def generar_servicio(tipo, base_imponible, igv=None):
    clave=tipo.upper().strip()
    if clave not in SERVICIOS:
        raise ValueError("Servicio no reconocido.")
    codigo,nombre=SERVICIOS[clave]
    if igv is None:
        igv=round(base_imponible*0.18,2)
    total=round(base_imponible+igv,2)
    return crear_asiento([
        {"codigo":codigo,"cuenta":nombre,"debe":base_imponible,"haber":0},
        {"codigo":"40111","cuenta":"IGV - Cuenta propia","debe":igv,"haber":0},
        {"codigo":"42120","cuenta":"Facturas emitidas por pagar","debe":0,"haber":total},
    ])
