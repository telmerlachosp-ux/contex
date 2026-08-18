from modelo_contable import crear_asiento


def _resolver_medio_pago_venta(medio_pago):
    medio = str(medio_pago).strip().upper()

    if medio in {"TRANSFERENCIA", "DEPOSITO", "DEPÓSITO", "CHEQUE", "TARJETA"}:
        return "10411", "Cuentas corrientes operativas"

    return "10111", "Caja"


def generar_venta(
    base_imponible,
    igv,
    total,
    condicion_cobro="CREDITO",
    medio_pago="EFECTIVO",
    costo_venta=None
):
    """
    Genera los asientos contables de una venta de mercaderías
    gravada con IGV:
    Asiento 1 - Por naturaleza (venta), SIEMPRE contra 12121
                Facturas por cobrar, sin importar la condición de pago.
    Asiento 2 - Por destino (costo de venta / salida de almacén).
    Asiento 3 - Cancelación de la cuenta por cobrar, SOLO si la
                condición de pago NO es crédito (es decir, se cobró
                al contado con el medio de pago indicado). Si es al
                crédito, este asiento no se genera: queda pendiente
                de cobro para una fecha posterior.

    Nota: si no se especifica costo_venta, se usa el mismo valor
    que la base imponible (venta sin margen), solo para pruebas.
    """
    if costo_venta is None:
        costo_venta = base_imponible

    glosa_venta = "Venta de mercadería según factura"
    glosa_costo = "Costo de venta y salida de mercadería del almacén"
    glosa_cobro = "Cobro de la factura por venta"

    cuentas = []

    cuentas.append({"asiento": 1, "codigo": "12121", "cuenta": "Facturas por cobrar", "debe": total, "haber": 0, "glosa": glosa_venta})
    cuentas.append({"asiento": 1, "codigo": "40111", "cuenta": "IGV - Cuenta propia", "debe": 0, "haber": igv, "glosa": glosa_venta})
    cuentas.append({"asiento": 1, "codigo": "70121", "cuenta": "Ventas", "debe": 0, "haber": base_imponible, "glosa": glosa_venta})

    cuentas.append({"asiento": 2, "codigo": "69111", "cuenta": "Costo de ventas", "debe": costo_venta, "haber": 0, "glosa": glosa_costo})
    cuentas.append({"asiento": 2, "codigo": "20111", "cuenta": "Mercaderías - Almacén", "debe": 0, "haber": costo_venta, "glosa": glosa_costo})

    if condicion_cobro.upper() != "CREDITO":
        codigo_pago, nombre_pago = _resolver_medio_pago_venta(medio_pago)
        cuentas.append({"asiento": 3, "codigo": codigo_pago, "cuenta": nombre_pago, "debe": total, "haber": 0, "glosa": glosa_cobro})
        cuentas.append({"asiento": 3, "codigo": "12121", "cuenta": "Facturas por cobrar", "debe": 0, "haber": total, "glosa": glosa_cobro})

    return crear_asiento(cuentas)
