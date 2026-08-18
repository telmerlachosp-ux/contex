from modelo_contable import crear_asiento

TASA_ONP = 0.13
TASA_ESSALUD = 0.09

DESTINOS = {
    "ADMINISTRACION": {"codigo": "94211", "nombre": "Gastos de administración - personal"},
    "VENTAS": {"codigo": "95211", "nombre": "Gastos de ventas - personal"},
}


def generar_planilla(
    sueldo_bruto,
    incluir_pago_trabajador=True,
    incluir_pago_sunat=True,
    porcentaje_administracion=100
):
    """
    Genera los asientos contables de una planilla de sueldos:
    Asiento 1 - Provisión de la planilla
    Asiento 2 - Pago del neto al trabajador (opcional)
    Asiento 3 - Pago de aportes a SUNAT (ONP + Essalud) (opcional)
    Asiento 4 - Destino: distribución del gasto por función, según
                el porcentaje de administración indicado (0-100).
                El resto va a ventas. Si es 100 o 0, se genera una
                sola línea; si es intermedio, se reparte en dos.
    """
    onp = round(sueldo_bruto * TASA_ONP, 2)
    essalud = round(sueldo_bruto * TASA_ESSALUD, 2)
    neto = round(sueldo_bruto - onp, 2)

    glosa_provision = "Provisión de planilla del período"
    glosa_pago_trabajador = "Pago de remuneraciones al trabajador"
    glosa_pago_sunat = "Pago de aportes ONP y Essalud a SUNAT"

    cuentas = []

    cuentas.append({"asiento": 1, "codigo": "62111", "cuenta": "Sueldos y salarios", "debe": sueldo_bruto, "haber": 0, "glosa": glosa_provision})
    cuentas.append({"asiento": 1, "codigo": "62711", "cuenta": "Essalud", "debe": essalud, "haber": 0, "glosa": glosa_provision})
    cuentas.append({"asiento": 1, "codigo": "40312", "cuenta": "ONP por pagar", "debe": 0, "haber": onp, "glosa": glosa_provision})
    cuentas.append({"asiento": 1, "codigo": "40311", "cuenta": "Essalud por pagar", "debe": 0, "haber": essalud, "glosa": glosa_provision})
    cuentas.append({"asiento": 1, "codigo": "41011", "cuenta": "Remuneraciones por pagar", "debe": 0, "haber": neto, "glosa": glosa_provision})

    if incluir_pago_trabajador:
        cuentas.append({"asiento": 2, "codigo": "41011", "cuenta": "Remuneraciones por pagar", "debe": neto, "haber": 0, "glosa": glosa_pago_trabajador})
        cuentas.append({"asiento": 2, "codigo": "10111", "cuenta": "Caja", "debe": 0, "haber": neto, "glosa": glosa_pago_trabajador})

    if incluir_pago_sunat:
        total_sunat = round(onp + essalud, 2)
        cuentas.append({"asiento": 3, "codigo": "40312", "cuenta": "ONP por pagar", "debe": onp, "haber": 0, "glosa": glosa_pago_sunat})
        cuentas.append({"asiento": 3, "codigo": "40311", "cuenta": "Essalud por pagar", "debe": essalud, "haber": 0, "glosa": glosa_pago_sunat})
        cuentas.append({"asiento": 3, "codigo": "10111", "cuenta": "Caja", "debe": 0, "haber": total_sunat, "glosa": glosa_pago_sunat})

    glosa_destino = "Distribución del gasto de planilla por función"
    gasto_total = round(sueldo_bruto + essalud, 2)
    porcentaje_admin = max(0, min(100, porcentaje_administracion))
    monto_admin = round(gasto_total * porcentaje_admin / 100, 2)
    monto_ventas = round(gasto_total - monto_admin, 2)

    if monto_admin > 0:
        cuentas.append({"asiento": 4, "codigo": DESTINOS["ADMINISTRACION"]["codigo"], "cuenta": DESTINOS["ADMINISTRACION"]["nombre"], "debe": monto_admin, "haber": 0, "glosa": glosa_destino})
    if monto_ventas > 0:
        cuentas.append({"asiento": 4, "codigo": DESTINOS["VENTAS"]["codigo"], "cuenta": DESTINOS["VENTAS"]["nombre"], "debe": monto_ventas, "haber": 0, "glosa": glosa_destino})

    cuentas.append({"asiento": 4, "codigo": "79111", "cuenta": "Cargas imputables a cuentas de costos y gastos", "debe": 0, "haber": gasto_total, "glosa": glosa_destino})

    return crear_asiento(cuentas)
