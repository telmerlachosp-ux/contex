from modelo_contable import crear_asiento

TASA_ONP = 0.13
TASA_ESSALUD = 0.09


def generar_planilla(
    sueldo_bruto,
    incluir_pago_trabajador=True,
    incluir_pago_sunat=True
):
    """
    Genera los asientos contables de una planilla de sueldos:
    Asiento 1 - Provisión de la planilla
    Asiento 2 - Pago del neto al trabajador (opcional)
    Asiento 3 - Pago de aportes a SUNAT (ONP + Essalud) (opcional)
    Asiento 4 - Destino: distribución del gasto por función
    """
    onp = round(sueldo_bruto * TASA_ONP, 2)
    essalud = round(sueldo_bruto * TASA_ESSALUD, 2)
    neto = round(sueldo_bruto - onp, 2)

    glosa_provision = "Provisión de planilla usando las cuentas 62111, 62711, 40312, 40311 y 41011"
    glosa_pago_trabajador = "Pago del neto de planilla al trabajador usando las cuentas 41011 y 10111"
    glosa_pago_sunat = "Pago de aportes ONP y Essalud a SUNAT usando las cuentas 40312, 40311 y 10111"
    glosa_destino = "Destino del gasto de planilla usando las cuentas 94311 y 79111"

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

    gasto_total = round(sueldo_bruto + essalud, 2)
    cuentas.append({"asiento": 4, "codigo": "94311", "cuenta": "Gastos de administración - sueldos", "debe": gasto_total, "haber": 0, "glosa": glosa_destino})
    cuentas.append({"asiento": 4, "codigo": "79111", "cuenta": "Cargas imputables a cuentas de costos y gastos", "debe": 0, "haber": gasto_total, "glosa": glosa_destino})

    return crear_asiento(cuentas)
