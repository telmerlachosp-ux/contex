import streamlit as st
import fitz  # PyMuPDF
import docx
import re
import base64
from google import genai

from interpretador_gemini import (
    extraer_datos_compra,
    extraer_datos_venta,
    extraer_datos_planilla,
    extraer_datos_depreciacion,
    extraer_datos_provision,
    extraer_datos_prestamo
)
from clasificador_gemini import clasificar_ejercicio
from generador_compras import generar_compra
from generador_ventas import generar_venta
from generador_planilla import generar_planilla
from generador_depreciacion import generar_depreciacion
from generador_provision import generar_provision
from generador_prestamos import generar_prestamo_desde_enunciado
from generador_excel import generar_excel_multiples_asientos


st.set_page_config(page_title="CONTEX - IA Contable", page_icon="📊")

st.title("📊 CONTEX")
st.write(
    "Sube tu monografía o ejercicio de contabilidad (PDF, Word o imagen) "
    "y descarga el Excel con los asientos resueltos."
)


# ==========================================
# EXTRACCIÓN DE TEXTO SEGÚN TIPO DE ARCHIVO
# ==========================================

def _extraer_texto_pdf(archivo):
    contenido = archivo.read()
    documento = fitz.open(stream=contenido, filetype="pdf")
    texto = ""
    for pagina in documento:
        texto += pagina.get_text()
    documento.close()
    return texto


def _extraer_texto_word(archivo):
    documento = docx.Document(archivo)
    parrafos = [parrafo.text for parrafo in documento.paragraphs]
    return "\n".join(parrafos)


def _extraer_texto_imagen(archivo, api_key):
    cliente = genai.Client(api_key=api_key)
    imagen_bytes = archivo.read()
    media_type = archivo.type if archivo.type else "image/png"
    imagen_base64 = base64.b64encode(imagen_bytes).decode("utf-8")

    interaction = cliente.interactions.create(
        model="gemini-3.5-flash-lite",
        input=[
            {
                "type": "text",
                "text": (
                    "Transcribe TODO el texto de esta imagen tal como "
                    "aparece, sin resumir ni interpretar. Es un ejercicio "
                    "o monografía de contabilidad."
                )
            },
            {
                "type": "image",
                "mime_type": media_type,
                "data": imagen_base64
            }
        ]
    )
    return interaction.output_text


def _extraer_texto_archivo(archivo, api_key):
    nombre = archivo.name.lower()

    if nombre.endswith(".pdf"):
        return _extraer_texto_pdf(archivo)

    if nombre.endswith(".docx"):
        return _extraer_texto_word(archivo)

    if nombre.endswith((".png", ".jpg", ".jpeg")):
        return _extraer_texto_imagen(archivo, api_key)

    raise ValueError("Tipo de archivo no soportado.")


# ==========================================
# DIVIDIR Y RESOLVER EJERCICIOS
# ==========================================

def _dividir_ejercicios(texto):
    """
    Divide un texto que puede traer VARIOS ejercicios numerados
    (1. ... 2. ... 3. ...) en una lista de ejercicios individuales.
    Si no encuentra numeración, devuelve el texto completo como
    un único ejercicio.
    """
    partes = re.split(r"(?m)^\s*\d+[\.\)]\s*", texto)
    ejercicios = [parte.strip() for parte in partes if parte.strip()]

    if not ejercicios:
        return [texto.strip()]

    return ejercicios


def _agrupar_por_asiento(cuentas):
    """
    Agrupa una lista plana de cuentas (cada una con "asiento" y
    "glosa") en bloques por número de asiento, usando la glosa
    real de cada bloque en vez de una etiqueta genérica.
    """
    bloques = []
    numero_actual = None
    bloque_actual = None

    for cuenta in cuentas:
        if cuenta["asiento"] != numero_actual:
            if bloque_actual is not None:
                bloques.append(bloque_actual)
            bloque_actual = {
                "tipo_asiento": cuenta.get("glosa", f"Asiento {cuenta['asiento']}"),
                "cuentas": [],
                "validacion": {}
            }
            numero_actual = cuenta["asiento"]
        bloque_actual["cuentas"].append(cuenta)

    if bloque_actual is not None:
        bloques.append(bloque_actual)

    return bloques


def _resolver_un_ejercicio(texto_ejercicio, api_key):
    """
    Clasifica y resuelve UN solo ejercicio. Devuelve
    (tipo_detectado, datos_generales, asientos_finales).
    """
    tipo_detectado = clasificar_ejercicio(texto_ejercicio, api_key)

    if tipo_detectado == "COMPRA":
        datos = extraer_datos_compra(texto_ejercicio, api_key)
        resultado = generar_compra(
            base_imponible=datos["base_imponible"],
            igv=datos["igv"],
            total=datos["total"],
            condicion_pago=datos["condicion_pago"]
        )
        return tipo_detectado, datos, _agrupar_por_asiento(resultado["cuentas"])

    if tipo_detectado == "VENTA":
        datos = extraer_datos_venta(texto_ejercicio, api_key)
        resultado = generar_venta(
            base_imponible=datos["base_imponible"],
            igv=datos["igv"],
            total=datos["total"],
            condicion_cobro=datos["condicion_cobro"]
        )
        return tipo_detectado, datos, _agrupar_por_asiento(resultado["cuentas"])

    if tipo_detectado == "PLANILLA":
        datos = extraer_datos_planilla(texto_ejercicio, api_key)
        resultado = generar_planilla(
            sueldo_bruto=datos["sueldo_bruto"],
            incluir_pago_trabajador=datos.get("incluir_pago_trabajador", True),
            incluir_pago_sunat=datos.get("incluir_pago_sunat", True),
            destino=datos.get("destino", "ADMINISTRACION")
        )
        return tipo_detectado, datos, _agrupar_por_asiento(resultado["cuentas"])

    if tipo_detectado == "DEPRECIACION":
        datos = extraer_datos_depreciacion(texto_ejercicio, api_key)
        resultado = generar_depreciacion(
            valor_activo=datos["valor_activo"],
            tipo_activo=datos.get("tipo_activo", "MAQUINARIA"),
            vida_util_anios=datos.get("vida_util_anios"),
            tasa_anual=datos.get("tasa_anual"),
            periodo=datos.get("periodo", "MENSUAL"),
            destino=datos.get("destino", "ADMINISTRACION")
        )
        return tipo_detectado, datos, _agrupar_por_asiento(resultado["cuentas"])

    if tipo_detectado == "PROVISION":
        datos = extraer_datos_provision(texto_ejercicio, api_key)
        resultado = generar_provision(
            monto=datos["monto"],
            destino=datos.get("destino", "ADMINISTRACION")
        )
        return tipo_detectado, datos, _agrupar_por_asiento(resultado["cuentas"])

    if tipo_detectado == "PRESTAMO":
        datos = extraer_datos_prestamo(texto_ejercicio, api_key)
        resultado_prestamo = generar_prestamo_desde_enunciado(
            texto_enunciado=texto_ejercicio,
            monto_prestamo=datos["monto_prestamo"],
            monto_interes=datos["monto_interes"],
            entidad_financiera=datos.get("entidad_financiera", ""),
            medio_pago=datos.get("medio_pago", "TRANSFERENCIA"),
            modalidad_interes=datos.get("modalidad_interes")
        )
        return tipo_detectado, datos, resultado_prestamo["asientos"]

    raise ValueError(f"Tipo de ejercicio no reconocido: {tipo_detectado}")


# ==========================================
# INTERFAZ: SUBIR ARCHIVO Y RESOLVER
# ==========================================

archivo_subido = st.file_uploader(
    "Sube tu archivo (PDF, Word o imagen)",
    type=["pdf", "docx", "png", "jpg", "jpeg"]
)

if archivo_subido is not None:
    if st.button("RESOLVER MONOGRAFÍA"):
        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            with st.spinner("Leyendo el archivo..."):
                texto_completo = _extraer_texto_archivo(archivo_subido, api_key)

            with st.expander("Ver texto extraído del archivo"):
                st.text(texto_completo)

            lista_ejercicios = _dividir_ejercicios(texto_completo)
            st.caption(f"Se detectaron {len(lista_ejercicios)} ejercicio(s) en el archivo.")

            historial_asientos = []
            historial_resumen = []

            for indice_ejercicio, texto_ejercicio in enumerate(lista_ejercicios, start=1):
                st.markdown(f"---\n#### Ejercicio {indice_ejercicio} de {len(lista_ejercicios)}")

                try:
                    with st.spinner(f"Resolviendo ejercicio {indice_ejercicio}..."):
                        tipo_detectado, datos_generales, asientos_finales = _resolver_un_ejercicio(
                            texto_ejercicio, api_key
                        )

                    st.info(f"Tipo detectado: **{tipo_detectado}**")
                    st.json(datos_generales)

                    debe_total = 0
                    haber_total = 0

                    for bloque in asientos_finales:
                        st.write(f"**{bloque['tipo_asiento']}**")
                        for cuenta in bloque["cuentas"]:
                            st.write(
                                cuenta["codigo"], "-", cuenta["cuenta"],
                                "| Debe:", cuenta["debe"],
                                "| Haber:", cuenta["haber"]
                            )
                            debe_total += cuenta["debe"]
                            haber_total += cuenta["haber"]

                    diferencia_total = round(debe_total - haber_total, 2)

                    if diferencia_total == 0:
                        st.success("✅ Este ejercicio está cuadrado.")
                    else:
                        st.error(f"❌ Este ejercicio NO cuadra. Diferencia: {diferencia_total}")

                    numero_global = len(historial_resumen) + 1
                    historial_asientos.extend(asientos_finales)
                    historial_resumen.append({
                        f"Ejercicio {numero_global} - Tipo": tipo_detectado,
                        f"Ejercicio {numero_global} - Datos": str(datos_generales)
                    })

                except Exception as error:
                    st.error(f"Ocurrió un error al resolver el ejercicio {indice_ejercicio}: {error}")

            if historial_asientos:
                resumen_acumulado = {}
                for entrada in historial_resumen:
                    resumen_acumulado.update(entrada)

                archivo_excel_final = generar_excel_multiples_asientos(
                    resumen_acumulado, historial_asientos
                )

                st.markdown("---")
                st.download_button(
                    label=f"📥 Descargar Excel completo ({len(historial_resumen)} ejercicio(s))",
                    data=archivo_excel_final,
                    file_name="ejercicios_resueltos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="descarga_final"
                )

        except Exception as error:
            st.error(f"Ocurrió un error al procesar el archivo: {error}")
