from modelo_contable import crear_asiento

DESTINOS = {
    "ADMINISTRACION": {"codigo": "94812", "nombre": "Gastos de administración - provisión cobranza dudosa"},
    "VENTAS": {"codigo": "95812", "nombre": "Gastos de ventas - provisión cobranza dudosa"},
}


def generar_provision(
    monto,
    porcentaje_administracion=100
):
    """
    Genera los asientos contables de la provisión (estimación) de
    cobranza dudosa sobre cuentas por cobrar comerciales a terceros:
    Asiento 1 - Provisión de cobranza dudosa
    Asiento 2 - Destino, repartido según porcentaje_administracion
                (0-100); el resto va a ventas.

    Cuentas según PCGE 2019 Modificado (MEF):
    687 Valuación de activos / 6871 Estimación de cuentas de cobranza dudosa
    19 Estimación de cuentas de cobranza dudosa / 191 Ctas. por cobrar
       comerciales - Terceros
    """
    glosa_provision = "Provisión de cobranza dudosa del período"

    cuentas = []

    cuentas.append({"asiento": 1, "codigo": "68711", "cuenta": "Estimación de cuentas de cobranza dudosa - Comerciales terceros", "debe": monto, "haber": 0, "glosa": glosa_provision})
    cuentas.append({"asiento": 1, "codigo": "19111", "cuenta": "Estimación de cuentas de cobranza dudosa - Facturas por cobrar", "debe": 0, "haber": monto, "glosa": glosa_provision})

    glosa_destino = "Distribución del gasto de provisión por función"
    porcentaje_admin = max(0, min(100, porcentaje_administracion))
    monto_admin = round(monto * porcentaje_admin / 100, 2)
    monto_ventas = round(monto - monto_admin, 2)

    if monto_admin > 0:
        cuentas.append({"asiento": 2, "codigo": DESTINOS["ADMINISTRACION"]["codigo"], "cuenta": DESTINOS["ADMINISTRACION"]["nombre"], "debe": monto_admin, "haber": 0, "glosa": glosa_destino})
    if monto_ventas > 0:
        cuentas.append({"asiento": 2, "codigo": DESTINOS["VENTAS"]["codigo"], "cuenta": DESTINOS["VENTAS"]["nombre"], "debe": monto_ventas, "haber": 0, "glosa": glosa_destino})

    cuentas.append({"asiento": 2, "codigo": "79111", "cuenta": "Cargas imputables a cuentas de costos y gastos", "debe": 0, "haber": monto, "glosa": glosa_destino})

    return crear_asiento(cuentas)
