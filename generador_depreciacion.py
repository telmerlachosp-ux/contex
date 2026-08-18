from modelo_contable import crear_asiento

TIPOS_ACTIVO = {
    "EDIFICACION": {"codigo_gasto": "68411", "codigo_acum": "39521", "nombre": "Edificaciones"},
    "MAQUINARIA": {"codigo_gasto": "68412", "codigo_acum": "39524", "nombre": "Maquinarias y equipos de explotación"},
    "VEHICULO": {"codigo_gasto": "68413", "codigo_acum": "39525", "nombre": "Unidades de transporte"},
    "MUEBLES": {"codigo_gasto": "68414", "codigo_acum": "39526", "nombre": "Muebles y enseres"},
    "EQUIPO_DIVERSO": {"codigo_gasto": "68415", "codigo_acum": "39527", "nombre": "Equipos diversos"},
}

DESTINOS = {
    "ADMINISTRACION": {"codigo": "94811", "nombre": "Gastos de administración - depreciación"},
    "VENTAS": {"codigo": "95811", "nombre": "Gastos de ventas - depreciación"},
}


def generar_depreciacion(
    valor_activo,
    tipo_activo="MAQUINARIA",
    vida_util_anios=None,
    tasa_anual=None,
    periodo="MENSUAL",
    porcentaje_administracion=100
):
    """
    Genera los asientos contables de la depreciación de un activo fijo:
    Asiento 1 - Depreciación del período
    Asiento 2 - Destino (ADMINISTRACION -> 94811, VENTAS -> 95811)

    Si no se da tasa_anual, se calcula a partir de vida_util_anios
    (tasa_anual = 1 / vida_util_anios).
    periodo puede ser "MENSUAL" (por defecto) o "ANUAL".

    Cuentas según PCGE 2019 Modificado (MEF):
    684 Depreciación de propiedad, planta y equipo - Costo (gasto)
    395 Depreciación acumulada de propiedad, planta y equipo - Costo

    Edificaciones: gasto 68411 / acumulada 39521
    Maquinaria y equipo: gasto 68412 / acumulada 39524
    Unidades de transporte: gasto 68413 / acumulada 39525
    Muebles y enseres: gasto 68414 / acumulada 39526
    Equipos diversos: gasto 68415 / acumulada 39527
    """
    if tasa_anual is None:
        if vida_util_anios is None:
            raise ValueError(
                "Se necesita vida_util_anios o tasa_anual para calcular la depreciación."
            )
        tasa_anual = 1 / vida_util_anios

    monto_anual = round(valor_activo * tasa_anual, 2)

    if periodo.upper() == "ANUAL":
        monto = monto_anual
    else:
        monto = round(monto_anual / 12, 2)

    tipo = TIPOS_ACTIVO.get(tipo_activo.upper(), TIPOS_ACTIVO["MAQUINARIA"])

    nombre_gasto = f"Depreciación - {tipo['nombre']}"
    nombre_acum = f"Depreciación acumulada - {tipo['nombre']}"

    glosa_deprec = f"Depreciación del período - {tipo['nombre']}"

    cuentas = []

    cuentas.append({"asiento": 1, "codigo": tipo["codigo_gasto"], "cuenta": nombre_gasto, "debe": monto, "haber": 0, "glosa": glosa_deprec})
    cuentas.append({"asiento": 1, "codigo": tipo["codigo_acum"], "cuenta": nombre_acum, "debe": 0, "haber": monto, "glosa": glosa_deprec})

    glosa_destino = "Distribución del gasto de depreciación por función"
    porcentaje_admin = max(0, min(100, porcentaje_administracion))
    monto_admin = round(monto * porcentaje_admin / 100, 2)
    monto_ventas = round(monto - monto_admin, 2)

    if monto_admin > 0:
        cuentas.append({"asiento": 2, "codigo": DESTINOS["ADMINISTRACION"]["codigo"], "cuenta": DESTINOS["ADMINISTRACION"]["nombre"], "debe": monto_admin, "haber": 0, "glosa": glosa_destino})
    if monto_ventas > 0:
        cuentas.append({"asiento": 2, "codigo": DESTINOS["VENTAS"]["codigo"], "cuenta": DESTINOS["VENTAS"]["nombre"], "debe": monto_ventas, "haber": 0, "glosa": glosa_destino})

    cuentas.append({"asiento": 2, "codigo": "79111", "cuenta": "Cargas imputables a cuentas de costos y gastos", "debe": 0, "haber": monto, "glosa": glosa_destino})

    return crear_asiento(cuentas)
