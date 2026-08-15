from motor_reglas import validar_asiento


# ==========================================
# CUENTAS DE ALQUILERES - PCGE 2019
# ==========================================

CUENTAS_ALQUILER = {
    "TERRENO": {
        "codigo": "6351",
        "cuenta": "Alquileres - Terrenos"
    },
    "EDIFICACION": {
        "codigo": "6352",
        "cuenta": "Alquileres - Edificaciones"
    },
    "MAQUINARIA": {
        "codigo": "6353",
        "cuenta": "Alquileres - Maquinarias y equipos de explotación"
    },
    "TRANSPORTE": {
        "codigo": "6354",
        "cuenta": "Alquileres - Equipo de transporte"
    },
    "MUEBLES": {
        "codigo": "6355",
        "cuenta": "Alquileres - Muebles y enseres"
    },
    "EQUIPOS": {
        "codigo": "6356",
        "cuenta": "Alquileres - Equipos diversos"
    }
}


def generar_registro_alquiler(
    tipo_bien,
    base_imponible,
    igv=0,
    total=None,
    condicion_pago="CREDITO",
    gravado_igv=True
):
    """
    Genera el asiento de registro/devengo de un alquiler.

    tipo_bien:
        TERRENO, EDIFICACION, MAQUINARIA,
        TRANSPORTE, MUEBLES o EQUIPOS.

    Para operaciones gravadas:
        base_imponible + IGV = total.
    """

    tipo_bien = str(tipo_bien).strip().upper()

    if tipo_bien not in CUENTAS_ALQUILER:
        raise ValueError(
            "Tipo de bien alquilado no reconocido. "
            "Use: TERRENO, EDIFICACION, MAQUINARIA, "
            "TRANSPORTE, MUEBLES o EQUIPOS."
        )

    base_imponible = float(base_imponible)
    igv = float(igv)

    if total is None:
        total = base_imponible + igv
    else:
        total = float(total)

    if gravado_igv:
        total_esperado = round(base_imponible + igv, 2)
        if round(total, 2) != total_esperado:
            raise ValueError(
                "El total no coincide con base imponible + IGV."
            )
    else:
        igv = 0.0
        total = base_imponible

    cuenta_alquiler = CUENTAS_ALQUILER[tipo_bien]

    cuentas = [
        {
            "codigo": cuenta_alquiler["codigo"],
            "cuenta": cuenta_alquiler["cuenta"],
            "debe": base_imponible,
            "haber": 0.0
        }
    ]

    if gravado_igv and igv > 0:
        cuentas.append(
            {
                "codigo": "40111",
                "cuenta": "IGV - Cuenta propia",
                "debe": igv,
                "haber": 0.0
            }
        )

    if str(condicion_pago).strip().upper() == "CREDITO":
        cuentas.append(
            {
                "codigo": "4212",
                "cuenta": (
                    "Facturas, boletas y otros "
                    "comprobantes por pagar - Emitidas"
                ),
                "debe": 0.0,
                "haber": total
            }
        )
    else:
        cuentas.append(
            {
                "codigo": "1041",
                "cuenta": "Cuentas corrientes operativas",
                "debe": 0.0,
                "haber": total
            }
        )

    resultado = validar_asiento(cuentas)

    return {
        "tipo_asiento": "REGISTRO",
        "tipo_bien": tipo_bien,
        "cuentas": cuentas,
        "validacion": resultado
    }


def generar_destino_alquiler(
    monto,
    cuenta_destino="94"
):
    """
    Genera el asiento de destino del gasto.

    El destino depende de la función del gasto.
    Por defecto se utiliza 94 como ejemplo.
    """

    monto = float(monto)

    cuentas = [
        {
            "codigo": str(cuenta_destino),
            "cuenta": "Gastos por función",
            "debe": monto,
            "haber": 0.0
        },
        {
            "codigo": "791",
            "cuenta": (
                "Cargas imputables a cuentas de costos "
                "y gastos"
            ),
            "debe": 0.0,
            "haber": monto
        }
    ]

    resultado = validar_asiento(cuentas)

    return {
        "tipo_asiento": "DESTINO",
        "cuentas": cuentas,
        "validacion": resultado
    }


def generar_pago_alquiler(
    total,
    medio_pago="TRANSFERENCIA"
):
    """
    Genera el asiento de cancelación de la cuenta por pagar.

    El pago se registra únicamente cuando existe
    una operación de cancelación.
    """

    total = float(total)
    medio_pago = str(medio_pago).strip().upper()

    if medio_pago == "EFECTIVO":
        codigo_pago = "1011"
        cuenta_pago = "Caja"

    elif medio_pago in {
        "TRANSFERENCIA",
        "TARJETA",
        "DEPOSITO",
        "DEPÓSITO",
        "ORDEN DE PAGO",
        "CHEQUE"
    }:
        codigo_pago = "1041"
        cuenta_pago = "Cuentas corrientes operativas"

    else:
        raise ValueError(
            "Medio de pago no reconocido."
        )

    cuentas = [
        {
            "codigo": "4212",
            "cuenta": (
                "Facturas, boletas y otros "
                "comprobantes por pagar - Emitidas"
            ),
            "debe": total,
            "haber": 0.0
        },
        {
            "codigo": codigo_pago,
            "cuenta": cuenta_pago,
            "debe": 0.0,
            "haber": total
        }
    ]

    resultado = validar_asiento(cuentas)

    return {
        "tipo_asiento": "PAGO",
        "medio_pago": medio_pago,
        "cuentas": cuentas,
        "validacion": resultado
    }


def generar_alquiler_anticipado(
    total,
    medio_pago="TRANSFERENCIA"
):
    """
    Registra un alquiler contratado/pagado por anticipado.

    El gasto no se reconoce todavía; se utiliza
    la cuenta 183 y posteriormente debe realizarse
    el devengo correspondiente.
    """

    total = float(total)
    medio_pago = str(medio_pago).strip().upper()

    if medio_pago == "EFECTIVO":
        codigo_pago = "1011"
        cuenta_pago = "Caja"
    elif medio_pago in {
        "TRANSFERENCIA",
        "TARJETA",
        "DEPOSITO",
        "DEPÓSITO",
        "ORDEN DE PAGO",
        "CHEQUE"
    }:
        codigo_pago = "1041"
        cuenta_pago = "Cuentas corrientes operativas"
    else:
        raise ValueError(
            "Medio de pago no reconocido."
        )

    cuentas = [
        {
            "codigo": "183",
            "cuenta": "Alquileres contratados por anticipado",
            "debe": total,
            "haber": 0.0
        },
        {
            "codigo": codigo_pago,
            "cuenta": cuenta_pago,
            "debe": 0.0,
            "haber": total
        }
    ]

    resultado = validar_asiento(cuentas)

    return {
        "tipo_asiento": "ALQUILER ANTICIPADO",
        "medio_pago": medio_pago,
        "cuentas": cuentas,
        "validacion": resultado
    }


def generar_devengo_alquiler_anticipado(
    monto,
    tipo_bien="EDIFICACION"
):
    """
    Reconoce como gasto el periodo de alquiler
    previamente registrado como anticipado.
    """

    tipo_bien = str(tipo_bien).strip().upper()

    if tipo_bien not in CUENTAS_ALQUILER:
        raise ValueError(
            "Tipo de bien alquilado no reconocido."
        )

    monto = float(monto)
    cuenta_alquiler = CUENTAS_ALQUILER[tipo_bien]

    cuentas = [
        {
            "codigo": cuenta_alquiler["codigo"],
            "cuenta": cuenta_alquiler["cuenta"],
            "debe": monto,
            "haber": 0.0
        },
        {
            "codigo": "183",
            "cuenta": "Alquileres contratados por anticipado",
            "debe": 0.0,
            "haber": monto
        }
    ]

    resultado = validar_asiento(cuentas)

    return {
        "tipo_asiento": "DEVENGO",
        "tipo_bien": tipo_bien,
        "cuentas": cuentas,
        "validacion": resultado
    }
