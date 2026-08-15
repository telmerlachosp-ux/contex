from modelo_contable import crear_asiento


def generar_compra(
    base_imponible,
    igv,
    total,
    condicion_pago="CREDITO"
):
    """
    Genera el asiento contable de una compra
    de mercaderías gravada con IGV, incluyendo
    el asiento de destino (entrada a almacén).
    """
    cuentas = [
        {
            "codigo": "6011",
            "cuenta": "Mercaderías",
            "debe": base_imponible,
            "haber": 0
        },
        {
            "codigo": "40111",
            "cuenta": "IGV - Cuenta propia",
            "debe": igv,
            "haber": 0
        }
    ]

    if condicion_pago.upper() == "CREDITO":
        cuentas.append(
            {
                "codigo": "4212",
                "cuenta": "Facturas por pagar",
                "debe": 0,
                "haber": total
            }
        )
    else:
        cuentas.append(
            {
                "codigo": "1011",
                "cuenta": "Caja",
                "debe": 0,
                "haber": total
            }
        )

    # -------------------------------------------------
    # ASIENTO DE DESTINO: entrada de mercadería al almacén
    # -------------------------------------------------
    cuentas.append(
        {
            "codigo": "20111",
            "cuenta": "Mercaderías - Almacén",
            "debe": base_imponible,
            "haber": 0
        }
    )
    cuentas.append(
        {
            "codigo": "61111",
            "cuenta": "Variación de mercaderías",
            "debe": 0,
            "haber": base_imponible
        }
    )
    return crear_asiento(cuentas)
