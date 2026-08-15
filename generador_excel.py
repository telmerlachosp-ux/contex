from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO
from datetime import date


def _normalizar_resultado(resultado):
    """
    Acepta dos formatos de 'resultado' y los deja iguales:

    Formato A (plano, como el de generar_compra original):
        {"cuentas": [...], "debe": x, "haber": y, "diferencia": z, "cuadrado": bool}

    Formato B (anidado, como el de los generadores nuevos:
    provisiones, constitución, préstamos):
        {"cuentas": [...], "validacion": {"debe": x, "haber": y,
                                           "diferencia": z, "cuadrado": bool}}

    Devuelve siempre el formato A.
    """

    if "validacion" in resultado:
        return {
            "cuentas": resultado["cuentas"],
            "debe": resultado["validacion"]["debe"],
            "haber": resultado["validacion"]["haber"],
            "diferencia": resultado["validacion"]["diferencia"],
            "cuadrado": resultado["validacion"]["cuadrado"]
        }

    return resultado


def _completar_asiento_y_glosa(cuentas, glosa_por_defecto):
    """
    Si las cuentas no traen 'asiento' o 'glosa' (como pasa hoy con
    generar_compra, generar_venta, y todos los generadores nuevos),
    se los agrega automáticamente: todas bajo el asiento N° 1, con
    la glosa indicada.

    Si YA traen 'asiento'/'glosa' (por ejemplo si en el futuro
    decides agregarlos desde app.py), se respetan tal cual.
    """

    cuentas_completas = []

    for cuenta in cuentas:
        nueva = dict(cuenta)
        nueva.setdefault("asiento", 1)
        nueva.setdefault("glosa", glosa_por_defecto)
        cuentas_completas.append(nueva)

    return cuentas_completas


def generar_excel_compra(datos_extraidos, resultado, glosa="Asiento contable"):
    """
    Recibe los datos identificados por la IA y el resultado del asiento,
    y devuelve un archivo Excel en memoria (listo para descargar),
    con formato de libro diario: el N° correlativo, la fecha y la glosa
    aparecen una sola vez por cada asiento.

    Funciona tanto con el formato plano de generar_compra/generar_venta
    como con el formato anidado (validacion) de los generadores nuevos.
    Si las cuentas no traen 'asiento'/'glosa', se completan solas.
    """

    resultado = _normalizar_resultado(resultado)
    cuentas_normalizadas = _completar_asiento_y_glosa(
        resultado["cuentas"], glosa
    )
    resultado = dict(resultado)
    resultado["cuentas"] = cuentas_normalizadas

    wb = Workbook()

    # -------------------------
    # HOJA 1: RESUMEN
    # -------------------------
    hoja_resumen = wb.active
    hoja_resumen.title = "Resumen"

    hoja_resumen["A1"] = "RESUMEN DEL EJERCICIO"
    hoja_resumen["A1"].font = Font(bold=True, size=14)

    hoja_resumen["A3"] = "Base imponible"
    hoja_resumen["B3"] = datos_extraidos.get("base_imponible", "")

    hoja_resumen["A4"] = "IGV"
    hoja_resumen["B4"] = datos_extraidos.get("igv", "")

    hoja_resumen["A5"] = "Total"
    hoja_resumen["B5"] = datos_extraidos.get("total", "")

    hoja_resumen["A6"] = "Condición de pago"
    hoja_resumen["B6"] = datos_extraidos.get(
        "condicion_pago", datos_extraidos.get("condicion_cobro", "")
    )

    hoja_resumen.column_dimensions["A"].width = 20
    hoja_resumen.column_dimensions["B"].width = 15

    # -------------------------
    # HOJA 2: LIBRO DIARIO (ASIENTOS)
    # -------------------------
    hoja_asiento = wb.create_sheet("Asientos")

    encabezados = ["N° Corr", "Fecha", "Glosa", "Código", "Denominación", "Debe", "Haber"]
    hoja_asiento.append(encabezados)

    for celda in hoja_asiento[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill(
            start_color="305496", end_color="305496", fill_type="solid"
        )
        celda.alignment = Alignment(horizontal="center", vertical="center")

    fecha_hoy = date.today().strftime("%d/%m/%Y")

    fila_actual = 2
    asiento_anterior = None
    fila_inicio_bloque = 2

    for cuenta in resultado["cuentas"]:
        numero_asiento = cuenta["asiento"]

        if numero_asiento != asiento_anterior:
            if asiento_anterior is not None:
                fila_fin_bloque = fila_actual - 1
                if fila_fin_bloque > fila_inicio_bloque:
                    for columna in [1, 2, 3]:
                        hoja_asiento.merge_cells(
                            start_row=fila_inicio_bloque,
                            start_column=columna,
                            end_row=fila_fin_bloque,
                            end_column=columna
                        )

            hoja_asiento.cell(row=fila_actual, column=1, value=numero_asiento)
            hoja_asiento.cell(row=fila_actual, column=2, value=fecha_hoy)
            hoja_asiento.cell(row=fila_actual, column=3, value=cuenta["glosa"])

            fila_inicio_bloque = fila_actual
            asiento_anterior = numero_asiento

        hoja_asiento.cell(row=fila_actual, column=4, value=cuenta["codigo"])
        hoja_asiento.cell(row=fila_actual, column=5, value=cuenta["cuenta"])
        hoja_asiento.cell(row=fila_actual, column=6, value=cuenta["debe"])
        hoja_asiento.cell(row=fila_actual, column=7, value=cuenta["haber"])

        fila_actual += 1

    fila_fin_bloque = fila_actual - 1
    if fila_fin_bloque > fila_inicio_bloque:
        for columna in [1, 2, 3]:
            hoja_asiento.merge_cells(
                start_row=fila_inicio_bloque,
                start_column=columna,
                end_row=fila_fin_bloque,
                end_column=columna
            )

    for fila in hoja_asiento.iter_rows(min_row=2, max_row=fila_actual - 1):
        for celda in fila:
            celda.alignment = Alignment(vertical="top", wrap_text=True)

    fila_total = fila_actual + 1
    hoja_asiento.cell(row=fila_total, column=5, value="TOTALES").font = Font(bold=True)
    hoja_asiento.cell(row=fila_total, column=6, value=resultado["debe"]).font = Font(bold=True)
    hoja_asiento.cell(row=fila_total, column=7, value=resultado["haber"]).font = Font(bold=True)

    fila_validacion = fila_total + 1
    texto_validacion = "CUADRADO" if resultado["cuadrado"] else "NO CUADRADO"
    hoja_asiento.cell(row=fila_validacion, column=5, value="Validación")
    hoja_asiento.cell(row=fila_validacion, column=6, value=texto_validacion)

    hoja_asiento.column_dimensions["A"].width = 10
    hoja_asiento.column_dimensions["B"].width = 12
    hoja_asiento.column_dimensions["C"].width = 45
    hoja_asiento.column_dimensions["D"].width = 12
    hoja_asiento.column_dimensions["E"].width = 28
    hoja_asiento.column_dimensions["F"].width = 15
    hoja_asiento.column_dimensions["G"].width = 15

    # -------------------------
    # GUARDAR EN MEMORIA
    # -------------------------
    archivo_en_memoria = BytesIO()
    wb.save(archivo_en_memoria)
    archivo_en_memoria.seek(0)

    return archivo_en_memoria


def generar_excel_multiples_asientos(datos_extraidos, lista_asientos):
    """
    Igual que generar_excel_compra, pero para generadores que
    devuelven VARIOS asientos de una vez (como
    generar_constitucion_completa o generar_prestamo_desde_enunciado,
    que devuelven una lista de asientos: suscripción, aporte,
    gastos, etc.)

    'lista_asientos' es la lista tal como la devuelven esos
    generadores: cada elemento con 'tipo_asiento', 'cuentas' y
    'validacion'.

    Cada asiento de la lista se numera correlativamente (1, 2, 3...)
    y usa su propio 'tipo_asiento' como glosa.
    """

    cuentas_combinadas = []
    total_debe = 0.0
    total_haber = 0.0

    for numero, asiento in enumerate(lista_asientos, start=1):
        glosa = asiento.get("tipo_asiento", f"Asiento {numero}")

        for cuenta in asiento["cuentas"]:
            nueva = dict(cuenta)
            nueva["asiento"] = numero
            nueva["glosa"] = glosa
            cuentas_combinadas.append(nueva)

        total_debe += asiento["validacion"]["debe"]
        total_haber += asiento["validacion"]["haber"]

    resultado_combinado = {
        "cuentas": cuentas_combinadas,
        "debe": round(total_debe, 2),
        "haber": round(total_haber, 2),
        "diferencia": round(total_debe - total_haber, 2),
        "cuadrado": round(total_debe - total_haber, 2) == 0
    }

    return generar_excel_compra(datos_extraidos, resultado_combinado)
