from modelo_contable import crear_asiento

DESTINOS = {
    "ADMINISTRACION": {"codigo": "94812", "nombre": "Gastos de administración - provisión cobranza dudosa"},
    "VENTAS": {"codigo": "95812", "nombre": "Gastos de ventas - provisión cobranza dudosa"},
}


def generar_provision(
    monto,
    destino="ADMINISTRACION"
):
    """
    Genera los asientos contables de la provisión (estimación) de
    cobranza dudosa sobre cuentas por cobrar comerciales a terceros:
    Asiento 1 - Provisión de cobranza dudosa
    Asiento 2 - Destino (ADMINISTRACION -> 94812, VENTAS -> 95812)

    Cuentas según PCGE 2019 Modificado (MEF):
    687 Valuación de activos / 6871 Estimación de cuentas de cobranza dudosa
    19 Estimación de cuentas de cobranza dudosa / 191 Ctas. por cobrar
       comerciales - Terceros
    """
    glosa_provision = "Provisión de cobranza dudosa usando las cuentas 68711 y 19111"

    cuentas = []

    cuentas.append({"asiento": 1, "codigo": "68711", "cuenta": "Estimación de cuentas de cobranza dudosa - Comerciales terceros", "debe": monto, "haber": 0, "glosa": glosa_provision})
    cuentas.append({"asiento": 1, "codigo": "19111", "cuenta": "Estimación de cuentas de cobranza dudosa - Facturas por cobrar", "debe": 0, "haber": monto, "glosa": glosa_provision})

    destino_info = DESTINOS.get(destino.upper(), DESTINOS["ADMINISTRACION"])
    glosa_destino = f"Destino de la provisión usando las cuentas {destino_info['codigo']} y 79111"

    cuentas.append({"asiento": 2, "codigo": destino_info["codigo"], "cuenta": destino_info["nombre"], "debe": monto, "haber": 0, "glosa": glosa_destino})
    cuentas.append({"asiento": 2, "codigo": "79111", "cuenta": "Cargas imputables a cuentas de costos y gastos", "debe": 0, "haber": monto, "glosa": glosa_destino})

    return crear_asiento(cuentas)
