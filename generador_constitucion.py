from motor_reglas import validar_asiento, determinar_igv


# ============================================================
# GENERADOR DE CONSTITUCION DE EMPRESA - PCGE MODIFICADO 2019
# ============================================================
#
# La constitución de una empresa contablemente pasa por
# 3 momentos distintos, que casi siempre se piden por
# separado en los ejercicios de clase:
#
#   1. SUSCRIPCION DE CAPITAL
#      Los socios se comprometen a aportar. Nace un
#      derecho de cobro contra ellos (cuenta 141) y se
#      reconoce el Capital Social (cuenta 501).
#
#   2. APORTE / INTEGRACION DE CAPITAL
#      Los socios entregan realmente el dinero o los
#      bienes. Se cancela la cuenta por cobrar 141 contra
#      Efectivo (10) o un Activo (33), según el tipo de
#      aporte.
#
#   3. GASTOS DE CONSTITUCION
#      Pagos notariales, registrales y legales para poder
#      inscribir la empresa (cuenta de gasto 63), pagados
#      en efectivo o banco.
#
# IMPORTANTE (criterio contable):
# Bajo NIC 38, los gastos de organización y constitución
# NO se capitalizan como intangible: se reconocen como
# gasto del periodo en que se incurren (cuenta 63 o 65).
# Por eso este motor NO ofrece la opción de activarlos.


TIPOS_APORTE = {
    "EFECTIVO": {
        "codigo": "10411",
        "cuenta": "Cuentas corrientes operativas - Moneda nacional"
    },
    "BIENES": {
        "codigo": "33311",
        "cuenta": "Maquinarias y equipos de explotación - Costo"
    },
    "MERCADERIAS": {
        "codigo": "60111",
        "cuenta": "Mercaderías manufacturadas - Terceros"
    }
}

CONCEPTOS_GASTO_CONSTITUCION = {
    "NOTARIALES": {
        "codigo": "63991",
        "cuenta": "Otros servicios prestados por terceros - Notariales"
    },
    "REGISTRALES": {
        "codigo": "63992",
        "cuenta": "Otros servicios prestados por terceros - Registrales (SUNARP)"
    },
    "LEGALES": {
        "codigo": "63241",
        "cuenta": "Asesoría y consultoría - Legal y societaria"
    },
    "OTROS": {
        "codigo": "63999",
        "cuenta": "Otros servicios prestados por terceros - Otros"
    }
}


def _validar_monto(monto):
    """Valida y normaliza un importe."""

    try:
        monto = float(monto)
    except (TypeError, ValueError):
        raise ValueError("El monto debe ser numérico.")

    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero.")

    return round(monto, 2)


def _obtener_tipo_aporte(tipo_aporte):
    """Devuelve la configuración del tipo de aporte."""

    tipo = str(tipo_aporte).strip().upper()

    if tipo not in TIPOS_APORTE:
        tipos = ", ".join(TIPOS_APORTE.keys())
        raise ValueError(
            f"Tipo de aporte no reconocido. Use uno de: {tipos}."
        )

    return tipo, TIPOS_APORTE[tipo]


def _obtener_concepto_gasto(concepto):
    """Devuelve la configuración del concepto de gasto."""

    tipo = str(concepto).strip().upper()

    if tipo not in CONCEPTOS_GASTO_CONSTITUCION:
        tipos = ", ".join(CONCEPTOS_GASTO_CONSTITUCION.keys())
        raise ValueError(
            f"Concepto de gasto no reconocido. Use uno de: {tipos}."
        )

    return tipo, CONCEPTOS_GASTO_CONSTITUCION[tipo]


def generar_suscripcion_capital(
    monto,
    razon_social=""
):
    """
    Genera el asiento de suscripción de capital social.

    Ejemplo:
        141 Cuentas por cobrar a los accionistas    DEBE
        501 Capital social                          HABER
    """

    monto = _validar_monto(monto)

    cuentas = [
        {
            "codigo": "14211",
            "cuenta": "Accionistas (socios)",
            "debe": monto,
            "haber": 0.0
        },
        {
            "codigo": "50111",
            "cuenta": "Acciones comunes (capital social)",
            "debe": 0.0,
            "haber": monto
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "SUSCRIPCION DE CAPITAL",
        "razon_social": str(razon_social).strip(),
        "monto": monto,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_aporte_capital(
    tipo_aporte,
    monto,
    detalle_bien=""
):
    """
    Genera el asiento de aporte/integración de capital,
    es decir, la entrega real de lo que los socios
    se comprometieron a aportar.

    Ejemplo (aporte en efectivo):
        1041 Cuentas corrientes operativas    DEBE
        1411 Accionistas (socios)             HABER
    """

    tipo, datos = _obtener_tipo_aporte(tipo_aporte)
    monto = _validar_monto(monto)

    cuenta_aporte = datos["cuenta"]

    if tipo != "EFECTIVO" and detalle_bien:
        cuenta_aporte = f"{cuenta_aporte} - {str(detalle_bien).strip()}"

    cuentas = [
        {
            "codigo": datos["codigo"],
            "cuenta": cuenta_aporte,
            "debe": monto,
            "haber": 0.0
        },
        {
            "codigo": "14211",
            "cuenta": "Accionistas (socios)",
            "debe": 0.0,
            "haber": monto
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "APORTE DE CAPITAL",
        "tipo_aporte": tipo,
        "detalle_bien": str(detalle_bien).strip(),
        "monto": monto,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_gastos_constitucion(
    concepto,
    base_imponible,
    incluir_igv=True,
    medio_pago="EFECTIVO"
):
    """
    Genera el asiento de gastos de constitución
    (notariales, registrales, legales, otros).

    Estos gastos se reconocen directamente como gasto
    del periodo (no se activan como intangible),
    conforme a NIC 38.

    Ejemplo con IGV (pago en efectivo):
        6329  Servicios notariales           DEBE
        40111 IGV - Cuenta propia            DEBE
        1011  Caja                           HABER
    """

    tipo, datos = _obtener_concepto_gasto(concepto)
    base_imponible = _validar_monto(base_imponible)

    igv_info = determinar_igv(
        "GRAVADA" if incluir_igv else "INAFECTA",
        base_imponible
    )

    total = igv_info["total"]

    medio = str(medio_pago).strip().upper()

    if medio == "EFECTIVO":
        codigo_pago = "10111"
        cuenta_pago = "Caja - Moneda nacional"
    elif medio in {"TRANSFERENCIA", "DEPOSITO", "DEPÓSITO", "CHEQUE", "TARJETA"}:
        codigo_pago = "10411"
        cuenta_pago = "Cuentas corrientes operativas - Moneda nacional"
    else:
        raise ValueError(
            "Medio de pago no reconocido. "
            "Use EFECTIVO, TRANSFERENCIA, DEPOSITO, CHEQUE o TARJETA."
        )

    cuentas = [
        {
            "codigo": datos["codigo"],
            "cuenta": datos["cuenta"],
            "debe": base_imponible,
            "haber": 0.0
        }
    ]

    if incluir_igv and igv_info["igv"] > 0:
        cuentas.append(
            {
                "codigo": "40111",
                "cuenta": "IGV - Cuenta propia",
                "debe": igv_info["igv"],
                "haber": 0.0
            }
        )

    cuentas.append(
        {
            "codigo": codigo_pago,
            "cuenta": cuenta_pago,
            "debe": 0.0,
            "haber": total
        }
    )

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "GASTOS DE CONSTITUCION",
        "concepto": tipo,
        "medio_pago": medio,
        "base_imponible": base_imponible,
        "igv": igv_info["igv"],
        "total": total,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_constitucion_completa(
    monto_capital,
    tipo_aporte="EFECTIVO",
    detalle_bien="",
    gastos=None,
    razon_social=""
):
    """
    Genera de un solo golpe la secuencia completa de
    constitución de empresa:
        1. Suscripción de capital
        2. Aporte de capital
        3. (Opcional) Gastos de constitución, uno o varios

    'gastos' es una lista de diccionarios, por ejemplo:
        [
            {"concepto": "NOTARIALES", "base_imponible": 500,
             "incluir_igv": True, "medio_pago": "EFECTIVO"},
            {"concepto": "REGISTRALES", "base_imponible": 300,
             "incluir_igv": False, "medio_pago": "EFECTIVO"}
        ]

    Devuelve una lista con cada asiento generado, en orden,
    lista para mostrarse o exportarse tal como los demás
    generadores del proyecto.
    """

    asientos = []

    asientos.append(
        generar_suscripcion_capital(monto_capital, razon_social)
    )

    asientos.append(
        generar_aporte_capital(tipo_aporte, monto_capital, detalle_bien)
    )

    if gastos:
        for gasto in gastos:
            asientos.append(
                generar_gastos_constitucion(
                    concepto=gasto.get("concepto", "OTROS"),
                    base_imponible=gasto.get("base_imponible"),
                    incluir_igv=gasto.get("incluir_igv", True),
                    medio_pago=gasto.get("medio_pago", "EFECTIVO")
                )
            )

    return asientos
