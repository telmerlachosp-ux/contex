from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO


def generar_excel_compra(datos_extraidos, resultado):
    """
    Recibe los datos identificados por la IA y el resultado del asiento,
    y devuelve un archivo Excel en memoria (listo para descargar).
    """
    wb = Workbook()

    # -------------------------
    # HOJA 1: RESUMEN
    # -------------------------
    hoja_resumen = wb.active
    hoja_resumen.title = "Resumen"

    hoja_resumen["A1"] = "RESUMEN DEL EJERCICIO"
    hoja_resumen["A1"].font = Font(bold=True, size=14)

    hoja_resumen["A3"] = "Base imponible"
    hoja_resumen["B3"] = datos_extraidos["base_imponible"]

    hoja_resumen["A4"] = "IGV"
    hoja_resumen["B4"] = datos_extraidos["igv"]

    hoja_resumen["A5"] = "Total"
    hoja_resumen["B5"] = datos_extraidos["total"]

    hoja_resumen["A6"] = "Condición de pago"
    hoja_resumen["B6"] = datos_extraidos["condicion_pago"]

    hoja_resumen.column_dimensions["A"].width = 20
    hoja_resumen.column_dimensions["B"].width = 15

    # -------------------------
    # HOJA 2: ASIENTO CONTABLE
    # -------------------------
    hoja_asiento = wb.create_sheet("Asientos")

    encabezados = ["Asiento", "Código", "Cuenta", "Debe", "Haber", "Glosa"]
    hoja_asiento.append(encabezados)

    for celda in hoja_asiento[1]:
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill(
            start_color="305496", end_color="305496", fill_type="solid"
        )
        celda.alignment = Alignment(horizontal="center")

    for cuenta in resultado["cuentas"]:
        hoja_asiento.append([
            cuenta["asiento"],
            cuenta["codigo"],
            cuenta["cuenta"],
            cuenta["debe"],
            cuenta["haber"],
            cuenta["glosa"]
        ])

    fila_total = hoja_asiento.max_row + 2
    hoja_asiento.cell(row=fila_total, column=3, value="TOTALES").font = Font(bold=True)
    hoja_asiento.cell(row=fila_total, column=4, value=resultado["debe"]).font = Font(bold=True)
    hoja_asiento.cell(row=fila_total, column=5, value=resultado["haber"]).font = Font(bold=True)

    fila_validacion = fila_total + 1
    texto_validacion = "CUADRADO ✅" if resultado["cuadrado"] else "NO CUADRADO ❌"
    hoja_asiento.cell(row=fila_validacion, column=3, value="Validación")
    hoja_asiento.cell(row=fila_validacion, column=4, value=texto_validacion)

    hoja_asiento.column_dimensions["A"].width = 12
    hoja_asiento.column_dimensions["B"].width = 15
    hoja_asiento.column_dimensions["C"].width = 30
    hoja_asiento.column_dimensions["D"].width = 15
    hoja_asiento.column_dimensions["E"].width = 15
    hoja_asiento.column_dimensions["F"].width = 60

    # -------------------------
    # GUARDAR EN MEMORIA
    # -------------------------
    archivo_en_memoria = BytesIO()
    wb.save(archivo_en_memoria)
    archivo_en_memoria.seek(0)

    return archivo_en_memoria
