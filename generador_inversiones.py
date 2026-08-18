from modelo_contable import crear_asiento

def generar_inversion_financiera(monto, descripcion="Otras inversiones financieras"):
    return crear_asiento([
        {"codigo":"11211","cuenta":descripcion+" - Costo","debe":monto,"haber":0},
        {"codigo":"10410","cuenta":"Cuentas corrientes operativas","debe":0,"haber":monto},
    ])
