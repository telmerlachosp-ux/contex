from motor_reglas import validar_asiento, determinar_igv


# ============================================================
# GENERADOR DE PRESTAMOS FINANCIEROS - PCGE MODIFICADO 2019
# ============================================================
#
# La cuenta 45 "Obligaciones financieras" registra los
# préstamos recibidos de entidades del sistema financiero.
#
#   451 Préstamos de instituciones financieras y otras entidades
#       4511 Instituciones financieras -> 45111 (5 dígitos)
#   455 Costos de financiación por pagar
#       4551 Préstamos de instituciones financieras y otras
#            entidades -> 45511 (5 dígitos)
#
# La cuenta 67 "Gastos financieros" registra el costo
# financiero del periodo:
#
#   673 Intereses por préstamos y otras obligaciones
#       6731 Préstamos de instituciones financieras y otras
#            entidades -> 67311 (5 dígitos)
#   679 Otros gastos financieros
#       6791 Gastos bancarios -> 67911 (5 dígitos)
#
# El motor genera:
#   1. Desembolso del préstamo.
#   2. Devengo de intereses del periodo.
#   3. Pago de cuota (capital + interés).
#   4. Gastos y comisiones bancarias del préstamo.
#
# IMPORTANTE:
# Los intereses bancarios están exonerados / no gravados
# con IGV en la mayoría de los casos. Las comisiones
# bancarias sí pueden estar gravadas, por eso esa función
# sí permite incluir IGV de forma opcional.


def _validar_monto(monto, nombre="El monto"):
    """Valida y normaliza un importe."""

    try:
        monto = float(monto)
    except (TypeError, ValueError):
        raise ValueError(f"{nombre} debe ser numérico.")

    if monto <= 0:
        raise ValueError(f"{nombre} debe ser mayor que cero.")

    return round(monto, 2)


def _resolver_medio_pago(medio_pago):
    """Devuelve código y nombre de cuenta según el medio de pago."""

    medio = str(medio_pago).strip().upper()

    if medio == "EFECTIVO":
        return medio, "10111", "Caja - Moneda nacional"

    if medio in {"TRANSFERENCIA", "DEPOSITO", "DEPÓSITO", "CHEQUE", "TARJETA"}:
        return medio, "10411", "Cuentas corrientes operativas - Moneda nacional"

    raise ValueError(
        "Medio de pago no reconocido. "
        "Use EFECTIVO, TRANSFERENCIA, DEPOSITO, CHEQUE o TARJETA."
    )


def generar_desembolso_prestamo(
    monto,
    entidad_financiera="",
    medio_pago="TRANSFERENCIA"
):
    """
    Genera el asiento de desembolso (obtención) de un
    préstamo financiero.

    Ejemplo:
        10411 Cuentas corrientes operativas   DEBE
        45111 Préstamo - Instituciones fin.   HABER
    """

    monto = _validar_monto(monto, "El monto del préstamo")
    medio, codigo_pago, cuenta_pago = _resolver_medio_pago(medio_pago)

    cuenta_prestamo = "Instituciones financieras"
    if entidad_financiera:
        cuenta_prestamo = f"{cuenta_prestamo} - {str(entidad_financiera).strip()}"

    cuentas = [
        {
            "codigo": codigo_pago,
            "cuenta": cuenta_pago,
            "debe": monto,
            "haber": 0.0
        },
        {
            "codigo": "45111",
            "cuenta": cuenta_prestamo,
            "debe": 0.0,
            "haber": monto
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "DESEMBOLSO DE PRESTAMO",
        "entidad_financiera": str(entidad_financiera).strip(),
        "medio_pago": medio,
        "monto": monto,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_devengo_interes(
    monto_interes
):
    """
    Genera el asiento de devengo de intereses del periodo,
    es decir, el gasto financiero ya generado aunque
    todavía no se haya pagado.

    Ejemplo:
        67311 Intereses por préstamos           DEBE
        45511 Costos de financiación por pagar  HABER
    """

    monto_interes = _validar_monto(monto_interes, "El monto del interés")

    cuentas = [
        {
            "codigo": "67311",
            "cuenta": "Intereses por préstamos de instituciones financieras",
            "debe": monto_interes,
            "haber": 0.0
        },
        {
            "codigo": "45511",
            "cuenta": "Costos de financiación por pagar",
            "debe": 0.0,
            "haber": monto_interes
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "DEVENGO DE INTERESES",
        "monto_interes": monto_interes,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_pago_cuota(
    monto_capital,
    monto_interes,
    interes_ya_devengado=True,
    medio_pago="TRANSFERENCIA"
):
    """
    Genera el asiento de pago de una cuota del préstamo
    (amortización de capital + interés).

    Si 'interes_ya_devengado' es True, se asume que el
    interés ya fue reconocido antes con
    generar_devengo_interes(), por lo que se cancela la
    cuenta 45511 (no se vuelve a reconocer el gasto).

    Si es False, el interés se reconoce como gasto en
    el mismo momento del pago (67311 directamente).

    Ejemplo (con devengo previo):
        45111 Préstamo (amortización capital)   DEBE
        45511 Costos de financiación por pagar  DEBE
        10411 Cuentas corrientes operativas     HABER
    """

    monto_capital = _validar_monto(monto_capital, "El monto de capital")
    monto_interes = _validar_monto(monto_interes, "El monto del interés")
    medio, codigo_pago, cuenta_pago = _resolver_medio_pago(medio_pago)

    total = round(monto_capital + monto_interes, 2)

    cuentas = [
        {
            "codigo": "45111",
            "cuenta": "Instituciones financieras (amortización de capital)",
            "debe": monto_capital,
            "haber": 0.0
        }
    ]

    if interes_ya_devengado:
        cuentas.append(
            {
                "codigo": "45511",
                "cuenta": "Costos de financiación por pagar",
                "debe": monto_interes,
                "haber": 0.0
            }
        )
    else:
        cuentas.append(
            {
                "codigo": "67311",
                "cuenta": "Intereses por préstamos de instituciones financieras",
                "debe": monto_interes,
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
        "tipo_asiento": "PAGO DE CUOTA DE PRESTAMO",
        "interes_ya_devengado": interes_ya_devengado,
        "medio_pago": medio,
        "monto_capital": monto_capital,
        "monto_interes": monto_interes,
        "total": total,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_gastos_bancarios(
    base_imponible,
    incluir_igv=False,
    medio_pago="TRANSFERENCIA"
):
    """
    Genera el asiento de gastos/comisiones bancarias
    asociadas al préstamo (comisión de estructuración,
    portes, etc.).

    Por defecto no incluye IGV, porque la mayoría de
    comisiones de entidades financieras están exoneradas.
    Si tu caso sí está gravado, usa incluir_igv=True.

    Ejemplo:
        67911 Gastos bancarios              DEBE
        10411 Cuentas corrientes operativas HABER
    """

    base_imponible = _validar_monto(base_imponible, "El monto de la comisión")
    medio, codigo_pago, cuenta_pago = _resolver_medio_pago(medio_pago)

    igv_info = determinar_igv(
        "GRAVADA" if incluir_igv else "EXONERADA",
        base_imponible
    )

    total = igv_info["total"]

    cuentas = [
        {
            "codigo": "67911",
            "cuenta": "Gastos bancarios",
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
        "tipo_asiento": "GASTOS BANCARIOS DEL PRESTAMO",
        "medio_pago": medio,
        "base_imponible": base_imponible,
        "igv": igv_info["igv"],
        "total": total,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_pago_interes_adelantado(
    monto_interes_total,
    medio_pago="TRANSFERENCIA"
):
    """
    Genera el asiento cuando el interés del préstamo se
    paga POR ADELANTADO (todo de una vez, al inicio).

    Ese interés NO es gasto inmediato: primero se reconoce
    como un activo (costo de financiación pagado por
    anticipado) y se va consumiendo mes a mes con
    generar_amortizacion_interes_adelantado().

    Ejemplo:
        18111 Costos de financiación por anticipado  DEBE
        10411 Cuentas corrientes operativas           HABER
    """

    monto_interes_total = _validar_monto(
        monto_interes_total, "El monto del interés adelantado"
    )
    medio, codigo_pago, cuenta_pago = _resolver_medio_pago(medio_pago)

    cuentas = [
        {
            "codigo": "18111",
            "cuenta": "Costos de financiación por anticipado",
            "debe": monto_interes_total,
            "haber": 0.0
        },
        {
            "codigo": codigo_pago,
            "cuenta": cuenta_pago,
            "debe": 0.0,
            "haber": monto_interes_total
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "PAGO DE INTERES POR ADELANTADO",
        "medio_pago": medio,
        "monto_interes_total": monto_interes_total,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_amortizacion_interes_adelantado(
    monto_cuota_mensual
):
    """
    Genera el asiento mensual que reconoce, ya como gasto
    del mes, la parte proporcional del interés que se
    pagó por adelantado.

    Se usa una vez al mes, tantas veces como meses tenga
    el préstamo, hasta agotar el saldo de 18111.

    Ejemplo:
        67311 Intereses por préstamos                DEBE
        18111 Costos de financiación por anticipado   HABER
    """

    monto_cuota_mensual = _validar_monto(
        monto_cuota_mensual, "El monto de la cuota mensual de interés"
    )

    cuentas = [
        {
            "codigo": "67311",
            "cuenta": "Intereses por préstamos de instituciones financieras",
            "debe": monto_cuota_mensual,
            "haber": 0.0
        },
        {
            "codigo": "18111",
            "cuenta": "Costos de financiación por anticipado",
            "debe": 0.0,
            "haber": monto_cuota_mensual
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "AMORTIZACION DE INTERES ADELANTADO",
        "monto_cuota_mensual": monto_cuota_mensual,
        "cuentas": cuentas,
        "validacion": validacion
    }


# ============================================================
# DETECCION DE LA MODALIDAD DE INTERES (a partir del texto)
# ============================================================
#
# Esta función lee el enunciado del ejercicio (texto libre,
# tal como lo escribe el estudiante o lo entrega el profesor)
# y decide si el interés es "ADELANTADO" o "VENCIDO"
# (mes a mes), según palabras clave.
#
# Es un detector basado en reglas (rápido, sin costo de API).
# Si en tu app ya usas interpretador_gemini.py para leer el
# enunciado completo, puedes pedirle a Gemini que devuelva
# el campo "modalidad_interes": "ADELANTADO" o "VENCIDO"
# directamente en su JSON de salida, y usar ese valor en vez
# de llamar a esta función. Esta función queda como respaldo
# o para validar lo que responda la IA.

_PALABRAS_ADELANTADO = [
    "por adelantado",
    "adelantado",
    "anticipado",
    "por anticipado",
    "al inicio del préstamo",
    "al inicio del prestamo",
    "se descuenta",
    "interés descontado",
    "interes descontado",
    "pagado de forma anticipada"
]

_PALABRAS_VENCIDO = [
    "mes a mes",
    "mensualmente",
    "cada mes",
    "al final de cada mes",
    "al vencimiento",
    "vencido",
    "en cuotas mensuales",
    "cuota mensual"
]


def detectar_modalidad_interes(texto_enunciado):
    """
    Analiza el texto del enunciado y determina si el
    interés del préstamo es ADELANTADO o VENCIDO
    (mes a mes).

    Devuelve un diccionario con la modalidad detectada,
    para que la app pueda decidir qué función usar, y
    para mostrarle al estudiante por qué se detectó así.

    Si no encuentra pistas claras, devuelve modalidad
    "INDEFINIDA" para que la app pida más datos en vez
    de asumir algo incorrecto.
    """

    texto = str(texto_enunciado).strip().lower()

    if not texto:
        return {
            "modalidad": "INDEFINIDA",
            "coincidencias": [],
            "observacion": "El enunciado está vacío."
        }

    coincidencias_adelantado = [
        palabra for palabra in _PALABRAS_ADELANTADO if palabra in texto
    ]
    coincidencias_vencido = [
        palabra for palabra in _PALABRAS_VENCIDO if palabra in texto
    ]

    if coincidencias_adelantado and not coincidencias_vencido:
        return {
            "modalidad": "ADELANTADO",
            "coincidencias": coincidencias_adelantado,
            "observacion": (
                "Se detectó que el interés se paga por "
                "adelantado. Se debe usar "
                "generar_pago_interes_adelantado() y luego "
                "generar_amortizacion_interes_adelantado() "
                "cada mes."
            )
        }

    if coincidencias_vencido and not coincidencias_adelantado:
        return {
            "modalidad": "VENCIDO",
            "coincidencias": coincidencias_vencido,
            "observacion": (
                "Se detectó que el interés se paga mes a "
                "mes (vencido). Se debe usar "
                "generar_devengo_interes() y/o "
                "generar_pago_cuota()."
            )
        }

    if coincidencias_adelantado and coincidencias_vencido:
        return {
            "modalidad": "INDEFINIDA",
            "coincidencias": coincidencias_adelantado + coincidencias_vencido,
            "observacion": (
                "El enunciado tiene señales de ambas "
                "modalidades a la vez. Revisa el texto o "
                "pídele al estudiante que aclare."
            )
        }

    return {
        "modalidad": "INDEFINIDA",
        "coincidencias": [],
        "observacion": (
            "No se encontraron palabras clave sobre la "
            "modalidad del interés. Por defecto, en la "
            "práctica contable se asume interés VENCIDO "
            "(mes a mes) salvo que el enunciado diga lo "
            "contrario."
        )
    }


def generar_prestamo_completo(
    monto_prestamo,
    entidad_financiera="",
    medio_pago="TRANSFERENCIA",
    gastos_bancarios=None
):
    """
    Genera de un solo golpe:
        1. El desembolso del préstamo.
        2. (Opcional) Los gastos/comisiones bancarias
           asociadas a la apertura del préstamo.

    'gastos_bancarios' es un diccionario opcional, ejemplo:
        {"base_imponible": 150, "incluir_igv": True,
         "medio_pago": "TRANSFERENCIA"}

    Devuelve una lista de asientos, en orden, lista para
    mostrarse o exportarse igual que los demás generadores.
    """

    asientos = []

    asientos.append(
        generar_desembolso_prestamo(
            monto_prestamo, entidad_financiera, medio_pago
        )
    )

    if gastos_bancarios:
        asientos.append(
            generar_gastos_bancarios(
                base_imponible=gastos_bancarios.get("base_imponible"),
                incluir_igv=gastos_bancarios.get("incluir_igv", False),
                medio_pago=gastos_bancarios.get("medio_pago", medio_pago)
            )
        )

    return asientos


def generar_prestamo_desde_enunciado(
    texto_enunciado,
    monto_prestamo,
    monto_interes,
    entidad_financiera="",
    medio_pago="TRANSFERENCIA",
    modalidad_interes=None
):
    """
    Punto de entrada "inteligente": lee el enunciado,
    detecta si el interés es ADELANTADO o VENCIDO, y arma
    automáticamente la secuencia de asientos correcta.

    Si ya sabes la modalidad (por ejemplo porque la
    detectó interpretador_gemini.py), pásala directo en
    'modalidad_interes' ("ADELANTADO" o "VENCIDO") y este
    motor no vuelve a analizar el texto.

    Devuelve un diccionario con:
        - la detección realizada (o la modalidad forzada)
        - la lista de asientos generados
    """

    if modalidad_interes:
        deteccion = {
            "modalidad": str(modalidad_interes).strip().upper(),
            "coincidencias": [],
            "observacion": "Modalidad indicada manualmente (o por la IA)."
        }
    else:
        deteccion = detectar_modalidad_interes(texto_enunciado)

    modalidad = deteccion["modalidad"]

    if modalidad == "INDEFINIDA":
        return {
            "deteccion": deteccion,
            "asientos": [],
            "requiere_aclaracion": True
        }

    asientos = [
        generar_desembolso_prestamo(
            monto_prestamo, entidad_financiera, medio_pago
        )
    ]

    if modalidad == "ADELANTADO":
        asientos.append(
            generar_pago_interes_adelantado(monto_interes, medio_pago)
        )
    elif modalidad == "VENCIDO":
        asientos.append(
            generar_devengo_interes(monto_interes)
        )
    else:
        raise ValueError(
            "Modalidad de interés no reconocida. "
            "Use 'ADELANTADO' o 'VENCIDO'."
        )

    return {
        "deteccion": deteccion,
        "asientos": asientos,
        "requiere_aclaracion": False
    }

        "deteccion": deteccion,
        "asientos": asientos,
        "requiere_aclaracion": False
    }
