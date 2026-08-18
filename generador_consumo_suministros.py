from modelo_contable import crear_asiento

def generar_consumo_suministros(monto):
    return crear_asiento([
        {"codigo":"65600","cuenta":"Suministros consumidos","debe":monto,"haber":0},
        {"codigo":"25250","cuenta":"Suministros - Útiles de escritorio","debe":0,"haber":monto},
    ])
