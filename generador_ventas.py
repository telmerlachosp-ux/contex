from modelo_contable import crear_asiento


def generar_venta(
    base_imponible,
    igv,
    total,
    condicion_cobro="CREDITO",
    costo_venta=None
):
    """
    Genera los asientos contables de una venta
    de mercaderías gravada con IGV:
    Asiento 1 - Por naturaleza (venta)
    Asiento 2 - Por destino (costo de venta / salida de almacén)
    Asiento 3 - Cobro de la venta (solo si es al crédito)

    Nota: si no se especifica costo_venta, se usa el mismo valor
    que la base imponible (venta sin margen), solo para pruebas.
    """
    if costo_venta is None:
        costo_venta = base_imponible

    glosa_venta = "Venta de mercadería según factura"
    glosa_costo = "Costo de venta y salida de mercadería del almacén"
    glosa_cobro = "Cobro de la factura por venta"

    cuentas = []

    if condicion_cobro.upper() == "CREDITO":
        cuentas.append({"asiento": 1, "codigo": "12121", "cuenta": "Facturas por cobrar", "debe": total, "haber": 0, "glosa": glosa_venta})
    else:
        cuentas.append({"asiento": 1, "codigo": "10111", "cuenta": "Caja", "debe": total, "haber": 0, "glosa": glosa_venta})

    cuentas.append({"asiento": 1, "codigo": "40111", "cuenta": "IGV - Cuenta propia", "debe": 0, "haber": igv, "glosa": glosa_venta})
    cuentas.append({"asiento": 1, "codigo": "70121", "cuenta": "Ventas", "debe": 0, "haber": base_imponible, "glosa": glosa_venta})

    cuentas.append({"asiento": 2, "codigo": "69111", "cuenta": "Costo de ventas", "debe": costo_venta, "haber": 0, "glosa": glosa_costo})
    cuentas.append({"asiento": 2, "codigo": "20111", "cuenta": "Mercaderías - Almacén", "debe": 0, "haber": costo_venta, "glosa": glosa_costo})

    if condicion_cobro.upper() == "CREDITO":
        cuentas.append({"asiento": 3, "codigo": "10111", "cuenta": "Caja", "debe": total, "haber": 0, "glosa": glosa_cobro})
        cuentas.append({"asiento": 3, "codigo": "12121", "cuenta": "Facturas por cobrar", "debe": 0, "haber": total, "glosa": glosa_cobro})

    return crear_asiento(cuentas)
