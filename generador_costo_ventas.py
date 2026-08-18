from modelo_contable import crear_asiento

def generar_costo_ventas(costo):
    return crear_asiento([
        {"codigo":"69120","cuenta":"Costo de ventas - mercaderías","debe":costo,"haber":0},
        {"codigo":"20111","cuenta":"Mercaderías - Costo","debe":0,"haber":costo},
    ])
