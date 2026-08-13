from typing import Optional


# ==========================================
# CONFIGURACIÓN TRIBUTARIA INICIAL
# ==========================================

TASA_IGV = 0.18
UMBRAL_BANCARIZACION_PEN = 2000.00


# ==========================================
# REGLAS DEL IGV
# ==========================================

def calcular_igv(base_imponible: float, tasa: float = TASA_IGV) -> float:
    """
    Calcula el IGV a partir de la base imponible.
    """

    if base_imponible < 0:
        raise ValueError("La base imponible no puede ser negativa.")

    return round(base_imponible * tasa, 2)


def calcular_total(
    base_imponible: float,
    igv: float
) -> float:
    """
    Calcula el importe total de una operación.
    """

    return round(base_imponible + igv, 2)


def determinar_igv(
    tratamiento_igv: str,
    base_imponible: float,
    tasa: float = TASA_IGV
) -> dict:
    """
    Determina el IGV según el tratamiento tributario
    indicado para la operación.
    """

    tratamiento = tratamiento_igv.strip().upper()

    if tratamiento == "GRAVADA":

        igv = calcular_igv(base_imponible, tasa)
        total = calcular_total(base_imponible, igv)

        return {
            "gravada_igv": True,
            "tratamiento_igv": "GRAVADA",
            "tasa_igv": tasa,
            "base_imponible": round(base_imponible, 2),
            "igv": igv,
            "total": total,
            "observacion": ""
        }

    elif tratamiento == "EXONERADA":

        return {
            "gravada_igv": False,
            "tratamiento_igv": "EXONERADA",
            "tasa_igv": 0.0,
            "base_imponible": round(base_imponible, 2),
            "igv": 0.0,
            "total": round(base_imponible, 2),
            "observacion": "Operación exonerada del IGV."
        }

    elif tratamiento == "INAFECTA":

        return {
            "gravada_igv": False,
            "tratamiento_igv": "INAFECTA",
            "tasa_igv": 0.0,
            "base_imponible": round(base_imponible, 2),
            "igv": 0.0,
            "total": round(base_imponible, 2),
            "observacion": "Operación inafecta del IGV."
        }

    else:

        return {
            "gravada_igv": None,
            "tratamiento_igv": "POR DETERMINAR",
            "tasa_igv": 0.0,
            "base_imponible": round(base_imponible, 2),
            "igv": 0.0,
            "total": round(base_imponible, 2),
            "observacion": (
                "No se puede determinar el tratamiento "
                "del IGV con la información disponible."
            )
        }


# ==========================================
# REGLAS DE BANCARIZACIÓN
# ==========================================

def verificar_bancarizacion(
    monto_pago: float,
    medio_pago: Optional[str] = None
) -> dict:
    """
    Verifica si un pago alcanza el umbral general
    de bancarización y si se indicó el medio de pago.

    Esta función NO inventa el medio de pago.
    """

    if monto_pago <= 0:

        return {
            "bancarizacion_obligatoria": False,
            "medio_pago": medio_pago,
            "observacion": "No se ha identificado un pago."
        }

    if monto_pago >= UMBRAL_BANCARIZACION_PEN:

        if medio_pago:

            return {
                "bancarizacion_obligatoria": True,
                "medio_pago": medio_pago,
                "observacion": (
                    "El pago alcanza el umbral general "
                    "de bancarización y se ha indicado "
                    "un medio de pago."
                )
            }

        return {
            "bancarizacion_obligatoria": True,
            "medio_pago": None,
            "observacion": (
                "El pago alcanza el umbral general "
                "de bancarización, pero el enunciado "
                "no especifica el medio de pago."
            )
        }

    return {
        "bancarizacion_obligatoria": False,
        "medio_pago": medio_pago,
        "observacion": (
            "El monto del pago se encuentra por debajo "
            "del umbral general de bancarización."
        )
    }


# ==========================================
# VALIDACIÓN DEL ASIENTO
# ==========================================

def validar_asiento(cuentas: list) -> dict:
    """
    Comprueba que el total del Debe sea igual
    al total del Haber.
    """

    total_debe = round(
        sum(float(cuenta.get("debe", 0)) for cuenta in cuentas),
        2
    )

    total_haber = round(
        sum(float(cuenta.get("haber", 0)) for cuenta in cuentas),
        2
    )

    diferencia = round(total_debe - total_haber, 2)

    return {
        "debe": total_debe,
        "haber": total_haber,
        "diferencia": diferencia,
        "cuadrado": diferencia == 0
    }
