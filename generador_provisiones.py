from motor_reglas import validar_asiento


# ============================================================
# GENERADOR DE PROVISIONES - PCGE MODIFICADO 2019
# ============================================================
#
# La cuenta 689 "Provisiones" comprende gastos asociados
# a pasivos cuya cuantía o vencimiento presenta incertidumbre.
#
# Tipos incluidos:
#   - LITIGIO
#   - DESMANTELAMIENTO
#   - REESTRUCTURACION
#   - MEDIO_AMBIENTE
#   - GARANTIA
#   - DERECHO_USO
#   - OTRA
#
# El motor genera:
#   1. Reconocimiento inicial de la provisión.
#   2. Destino del gasto.
#   3. Aplicación/pago de la provisión.
#   4. Reversión de una provisión.
#   5. Actualización financiera.
#
# IMPORTANTE:
# La cobranza dudosa no se trata aquí como provisión de la
# cuenta 689. En el PCGE se trata mediante la cuenta 687 y
# la cuenta 19. Por eso se mantiene separada.


TIPOS_PROVISION = {
    "LITIGIO": {
        "gasto": "68911",
        "cuenta_gasto": "Provisión para litigios - Costo",
        "pasivo": "4811",
        "cuenta_pasivo": "Provisión para litigios"
    },
    "DESMANTELAMIENTO": {
        "gasto": "68921",
        "cuenta_gasto": (
            "Provisión por desmantelamiento, retiro "
            "o rehabilitación del inmovilizado - Costo"
        ),
        "pasivo": "4821",
        "cuenta_pasivo": (
            "Provisión por desmantelamiento, retiro "
            "o rehabilitación del inmovilizado"
        )
    },
    "REESTRUCTURACION": {
        "gasto": "6893",
        "cuenta_gasto": "Provisión para reestructuraciones",
        "pasivo": "483",
        "cuenta_pasivo": "Provisión para reestructuraciones"
    },
    "MEDIO_AMBIENTE": {
        "gasto": "68941",
        "cuenta_gasto": (
            "Provisión para protección y remediación "
            "del medio ambiente - Costo"
        ),
        "pasivo": "4841",
        "cuenta_pasivo": (
            "Provisión para protección y remediación "
            "del medio ambiente"
        )
    },
    "GARANTIA": {
        "gasto": "68961",
        "cuenta_gasto": "Provisión para garantías - Costo",
        "pasivo": "4861",
        "cuenta_pasivo": "Provisión para garantías"
    },
    "DERECHO_USO": {
        "gasto": "68971",
        "cuenta_gasto": (
            "Provisión por activos por derecho de uso "
            "arrendamiento operativo"
        ),
        "pasivo": "4871",
        "cuenta_pasivo": (
            "Provisión por activos por derecho de uso"
        )
    },
    "OTRA": {
        "gasto": "6899",
        "cuenta_gasto": "Otras provisiones",
        "pasivo": "489",
        "cuenta_pasivo": "Otras provisiones"
    }
}


def _obtener_tipo(tipo_provision):
    """Devuelve la configuración del tipo de provisión."""

    tipo = str(tipo_provision).strip().upper()

    if tipo not in TIPOS_PROVISION:
        tipos = ", ".join(TIPOS_PROVISION.keys())

        raise ValueError(
            "Tipo de provisión no reconocido. "
            f"Use uno de: {tipos}."
        )

    return tipo, TIPOS_PROVISION[tipo]


def _validar_monto(monto):
    """Valida y normaliza el importe."""

    try:
        monto = float(monto)
    except (TypeError, ValueError):
        raise ValueError("El monto de la provisión debe ser numérico.")

    if monto <= 0:
        raise ValueError(
            "El monto de la provisión debe ser mayor que cero."
        )

    return round(monto, 2)


def generar_registro_provision(
    tipo_provision,
    monto
):
    """
    Genera el asiento de reconocimiento inicial de una provisión.

    Ejemplo:
        68911 Provisión para litigios - Costo     DEBE
        4811  Provisión para litigios             HABER
    """

    tipo, datos = _obtener_tipo(tipo_provision)
    monto = _validar_monto(monto)

    cuentas = [
        {
            "codigo": datos["gasto"],
            "cuenta": datos["cuenta_gasto"],
            "debe": monto,
            "haber": 0.0
        },
        {
            "codigo": datos["pasivo"],
            "cuenta": datos["cuenta_pasivo"],
            "debe": 0.0,
            "haber": monto
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "REGISTRO DE PROVISION",
        "tipo_provision": tipo,
        "monto": monto,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_destino_provision(
    monto,
    cuenta_destino="94"
):
    """
    Genera el destino del gasto de la provisión.

    En provisiones, la cuenta de transferencia utilizada
    es 78 - Cargas cubiertas por provisiones.

    El destino puede ser, por ejemplo:
        94 Gastos administrativos
        95 Gastos de ventas
        92 Costos de producción
    """

    monto = _validar_monto(monto)

    cuenta_destino = str(cuenta_destino).strip()

    if not cuenta_destino:
        raise ValueError(
            "Debe indicar la cuenta de destino."
        )

    cuentas = [
        {
            "codigo": cuenta_destino,
            "cuenta": "Gastos por función / costo",
            "debe": monto,
            "haber": 0.0
        },
        {
            "codigo": "781",
            "cuenta": "Cargas cubiertas por provisiones",
            "debe": 0.0,
            "haber": monto
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "DESTINO DE PROVISION",
        "monto": monto,
        "cuenta_destino": cuenta_destino,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_aplicacion_provision(
    tipo_provision,
    monto,
    medio_pago="TRANSFERENCIA"
):
    """
    Genera la aplicación/cancelación de una provisión
    cuando ocurre el hecho previsto.

    Ejemplo para una provisión que se cancela mediante banco:
        4811 Provisión para litigios        DEBE
        1041 Cuentas corrientes            HABER

    No vuelve a reconocer el gasto, porque el gasto
    ya fue reconocido al crear la provisión.
    """

    tipo, datos = _obtener_tipo(tipo_provision)
    monto = _validar_monto(monto)

    medio = str(medio_pago).strip().upper()

    if medio == "EFECTIVO":
        codigo_pago = "1011"
        cuenta_pago = "Caja"

    elif medio in {
        "TRANSFERENCIA",
        "DEPOSITO",
        "DEPÓSITO",
        "CHEQUE",
        "TARJETA"
    }:
        codigo_pago = "1041"
        cuenta_pago = "Cuentas corrientes operativas"

    else:
        raise ValueError(
            "Medio de pago no reconocido. "
            "Use EFECTIVO, TRANSFERENCIA, DEPOSITO, "
            "CHEQUE o TARJETA."
        )

    cuentas = [
        {
            "codigo": datos["pasivo"],
            "cuenta": datos["cuenta_pasivo"],
            "debe": monto,
            "haber": 0.0
        },
        {
            "codigo": codigo_pago,
            "cuenta": cuenta_pago,
            "debe": 0.0,
            "haber": monto
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "APLICACION / CANCELACION DE PROVISION",
        "tipo_provision": tipo,
        "medio_pago": medio,
        "monto": monto,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_reversion_provision(
    tipo_provision,
    monto
):
    """
    Genera la reversión de una provisión reconocida
    previamente cuando corresponde disminuirla o eliminarla.

    La reversión se presenta en sentido contrario
    al reconocimiento inicial.
    """

    tipo, datos = _obtener_tipo(tipo_provision)
    monto = _validar_monto(monto)

    cuentas = [
        {
            "codigo": datos["pasivo"],
            "cuenta": datos["cuenta_pasivo"],
            "debe": monto,
            "haber": 0.0
        },
        {
            "codigo": datos["gasto"],
            "cuenta": datos["cuenta_gasto"],
            "debe": 0.0,
            "haber": monto
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "REVERSIÓN DE PROVISION",
        "tipo_provision": tipo,
        "monto": monto,
        "cuentas": cuentas,
        "validacion": validacion
    }


def generar_actualizacion_financiera(
    tipo_provision,
    monto
):
    """
    Genera el asiento de actualización financiera
    de una provisión cuando corresponde.

    La actualización se registra en la divisionaria
    de actualización financiera de la cuenta 689
    y aumenta el pasivo relacionado.

    Este cálculo requiere que el importe de actualización
    ya haya sido determinado previamente.
    """

    tipo, datos = _obtener_tipo(tipo_provision)
    monto = _validar_monto(monto)

    if tipo == "LITIGIO":
        codigo_gasto = "68912"
        cuenta_gasto = "Provisión para litigios - Actualización financiera"

    elif tipo == "DESMANTELAMIENTO":
        codigo_gasto = "68922"
        cuenta_gasto = (
            "Provisión por desmantelamiento, retiro "
            "o rehabilitación del inmovilizado - "
            "Actualización financiera"
        )

    elif tipo == "MEDIO_AMBIENTE":
        codigo_gasto = "68942"
        cuenta_gasto = (
            "Provisión para protección y remediación "
            "del medio ambiente - Actualización financiera"
        )

    elif tipo == "GARANTIA":
        codigo_gasto = "68962"
        cuenta_gasto = "Provisión para garantías - Actualización financiera"

    elif tipo == "DERECHO_USO":
        codigo_gasto = "68972"
        cuenta_gasto = (
            "Provisión por activos por derecho de uso "
            "arrendamiento operativo - Actualización financiera"
        )

    else:
        raise ValueError(
            "Este tipo de provisión no tiene una "
            "divisionaria específica de actualización "
            "financiera en este motor."
        )

    cuentas = [
        {
            "codigo": codigo_gasto,
            "cuenta": cuenta_gasto,
            "debe": monto,
            "haber": 0.0
        },
        {
            "codigo": datos["pasivo"],
            "cuenta": datos["cuenta_pasivo"],
            "debe": 0.0,
            "haber": monto
        }
    ]

    validacion = validar_asiento(cuentas)

    return {
        "tipo_asiento": "ACTUALIZACION FINANCIERA",
        "tipo_provision": tipo,
        "monto": monto,
        "cuentas": cuentas,
        "validacion": validacion
    }
