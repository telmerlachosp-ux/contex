from modelo_contable import crear_asiento


def generar_compra(
    base_imponible,
    igv,
    total,
    condicion_pago="CREDITO"
):
    """
    Genera los asientos contables de una compra
    de mercaderías gravada con IGV:
    Asiento 1 - Por naturaleza (compra)
    Asiento 2 - Por destino (ingreso a almacén)
    """
    glosa_compra = "Compra de mercadería usando las cuentas 60111, 40111 y 42121"
    glosa_almacen = "Ingreso de mercadería al almacén usando las cuentas 20111 y 61111"

    cuentas = [
        {
            "asiento": 1,
            "codigo": "60111",
            "cuenta": "Mercaderías",
            "debe": base_imponible,
            "haber": 0,
            "glosa": glosa_compra
        },
        {
            "asiento": 1,
            "codigo": "40111",
            "cuenta": "IGV - Cuenta propia",
            "debe": igv,
            "haber": 0,
            "glosa": glosa_compra
        }
    ]

    if condicion_pago.upper() == "CREDITO":
        cuentas.append(
            {
                "asiento": 1,
                "codigo": "42121",
                "cuenta": "Facturas por pagar",
                "debe": 0,
                "haber": total,
                "glosa": glosa_compra
            }
        )
    else:
        cuentas.append(
            {
                "asiento": 1,
                "codigo": "1011",
                "cuenta": "Caja",
                "debe": 0,
                "haber": total,
                "glosa": glosa_compra
            }
        )

    cuentas.append(
        {
            "asiento": 2,
            "codigo": "20111",
            "cuenta": "Mercaderías - Almacén",
            "debe": base_imponible,
            "haber": 0,
            "glosa": glosa_almacen
        }
    )
  cuentas.append(
        {
            "asiento": 2,
            "codigo": "61111",
            "cuenta": "Variación de mercaderías",
            "debe": 0,
            "haber": base_imponible,
            "glosa": glosa_almacen
        }
    )

    return crear_asiento(cuentas)
