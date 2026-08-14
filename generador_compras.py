from modelo_contable import crear_asiento


def generar_compra(
    base_imponible,
    igv,
    total,
    condicion_pago="CREDITO"
):
    """
    Genera el asiento contable de una compra
    de mercaderías gravada con IGV.
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

    return crear_asiento(cuentas)
