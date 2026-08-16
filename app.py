import streamlit as st
import fitz
from google import genai

from motor_reglas import (
    determinar_igv,
    verificar_bancarizacion,
    validar_asiento
)


# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="CONTEX",
    page_icon="📚",
    layout="centered"
)


# ==========================================
# MEMORIA DE CONTEX
# ==========================================

if "texto_completo" not in st.session_state:
    st.session_state.texto_completo = ""

if "resultado_ia" not in st.session_state:
    st.session_state.resultado_ia = ""


# ==========================================
# ENCABEZADO
# ==========================================

st.title("CONTEX")

st.subheader(
    "Asistente contable con inteligencia artificial"
)

st.write(
    "Sube una monografía o ejercicio contable "
    "y CONTEX analizará su contenido."
)


# ==========================================
# CARGAR PDF
# ==========================================

archivo = st.file_uploader(
    "Selecciona tu archivo PDF",
    type=["pdf"]
)


if archivo is not None:

    st.success(
        f"Archivo cargado: {archivo.name}"
    )

    # ======================================
    # LEER DOCUMENTO
    # ======================================

    if st.button("LEER DOCUMENTO"):

        try:

            archivo_bytes = archivo.getvalue()

            documento = fitz.open(
                stream=archivo_bytes,
                filetype="pdf"
            )

            texto_completo = ""

            for numero_pagina, pagina in enumerate(
                documento,
                start=1
            ):

                texto_pagina = pagina.get_text()

                texto_completo += (
                    f"\n\n--- PÁGINA {numero_pagina} ---\n\n"
                    + texto_pagina
                )

            documento.close()

            # Guardar el texto en la memoria de CONTEX
            st.session_state.texto_completo = (
                texto_completo
            )

            # Limpiar resultado anterior
            st.session_state.resultado_ia = ""

        except Exception as error:

            st.error(
                f"No se pudo leer el documento: {error}"
            )


# ==========================================
# MOSTRAR DOCUMENTO LEÍDO
# ==========================================

if st.session_state.texto_completo.strip():

    st.success(
        "Documento leído correctamente."
    )

    st.subheader(
        "📄 Texto extraído del documento"
    )

    st.text_area(
        "Contenido detectado:",
        st.session_state.texto_completo,
        height=500
    )

    # ======================================
    # ANALIZAR CON GEMINI
    # ======================================

    st.divider()

    st.subheader(
        "🤖 Análisis contable con CONTEX"
    )

    if st.button("ANALIZAR DOCUMENTO"):

        try:

            api_key = st.secrets[
                "GEMINI_API_KEY"
            ]

            cliente = genai.Client(
                api_key=api_key
            )

            instrucciones = """
Eres CONTEX, un asistente especializado
en contabilidad peruana para estudiantes
de contabilidad.

Analiza cuidadosamente el documento.

Identifica las operaciones contables
que aparecen en el documento.

NO inventes información.

Para cada operación identifica:

- número de operación
- fecha
- tipo de operación
- descripción
- importe
- moneda
- base imponible
- tratamiento del IGV
- IGV
- total
- condición de pago
- medio de pago
- observaciones

Tipos de operación:

APERTURA
COMPRA
VENTA
COBRO
PAGO
OTRA

Tratamiento del IGV:

GRAVADA
EXONERADA
INAFECTA
NO ESPECIFICADA

Si un dato no aparece en el documento,
indica "NO ESPECIFICADO".

Ten presente las reglas de contabilidad
peruana y las reglas previamente establecidas
por CONTEX.

Respecto a la bancarización:

Si una operación requiere medio de pago
según las reglas establecidas por CONTEX
y el documento no especifica el medio,
indícalo como "NO ESPECIFICADO" y señala
la observación correspondiente.

Devuelve el resultado de forma clara,
ordenada y estructurada.

DOCUMENTO:
"""

            contenido = (
                instrucciones
                + "\n\n"
                + st.session_state.texto_completo
            )

            with st.spinner(
                "CONTEX está analizando el documento..."
            ):

                interaction = cliente.interactions.create(
                    model="gemini-3.5-flash-lite",
                    input=contenido
                )

                resultado = interaction.output_text

            st.session_state.resultado_ia = resultado

            st.success(
                "Documento analizado correctamente."
            )

        except Exception as error:

            st.error(
                f"No se pudo analizar el documento: {error}"
            )


# ==========================================
# MOSTRAR RESULTADO DE GEMINI
# ==========================================

if st.session_state.resultado_ia:

    st.subheader(
        "📊 Resultado del análisis"
    )

    st.text_area(
        "Análisis generado por CONTEX:",
        st.session_state.resultado_ia,
        height=600
    )


# ==========================================
# PRUEBA DEL MOTOR CONTABLE
# ==========================================

st.divider()

st.subheader(
    "🧪 Prueba del motor de CONTEX"
)


if st.button("PROBAR MOTOR"):

    resultado_igv = determinar_igv(
        tratamiento_igv="GRAVADA",
        base_imponible=10000
    )

    resultado_bancarizacion = verificar_bancarizacion(
        monto_pago=5000,
        medio_pago=None
    )

    cuentas = [

        {
            "codigo": "6011",
            "cuenta": "Mercaderías",
            "debe": 10000,
            "haber": 0
        },

        {
            "codigo": "40111",
            "cuenta": "IGV",
            "debe": 1800,
            "haber": 0
        },

        {
            "codigo": "4212",
            "cuenta": "Facturas por pagar",
            "debe": 0,
            "haber": 11800
        }

    ]

    resultado_validacion = validar_asiento(
        cuentas
    )

    st.write("### Resultado del IGV")

    st.write(
        "Base imponible:",
        resultado_igv["base_imponible"]
    )

    st.write(
        "IGV:",
        resultado_igv["igv"]
    )

    st.write(
        "Total:",
        resultado_igv["total"]
    )

    st.write(
        "### Resultado de bancarización"
    )

    st.write(
        "¿Obligatoria?:",
        resultado_bancarizacion[
            "bancarizacion_obligatoria"
        ]
    )

    st.write(
        "Medio de pago:",
        resultado_bancarizacion[
            "medio_pago"
        ]
    )

    st.warning(
        resultado_bancarizacion[
            "observacion"
        ]
    )

    st.write(
        "### Validación del asiento"
    )

    st.write(
        "Debe:",
        resultado_validacion["debe"]
    )

    st.write(
        "Haber:",
        resultado_validacion["haber"]
    )

    st.write(
        "Diferencia:",
        resultado_validacion["diferencia"]
    )

    if resultado_validacion["cuadrado"]:

        st.success(
            "✅ El asiento está cuadrado."
        )

    else:

        st.error(
            "❌ El asiento NO está cuadrado."
        )


# ==========================================
# PRUEBA DE GEMINI
# ==========================================

st.divider()

st.subheader(
    "🤖 Prueba de conexión con Gemini"
)


if st.button("PROBAR GEMINI"):

    try:

        api_key = st.secrets[
            "GEMINI_API_KEY"
        ]

        cliente = genai.Client(
            api_key=api_key
        )

        interaction = cliente.interactions.create(
            model="gemini-3.5-flash-lite",
            input="Responde únicamente: CONEXIÓN CORRECTA"
        )

        st.success(
            "Gemini está conectado correctamente."
        )

        st.write(
            "Respuesta de Gemini:"
        )

        st.write(
            interaction.output_text
        )

    except Exception as error:

        st.error(
            f"No se pudo conectar con Gemini: {error}"
        )
# -------------------------------------------------
# PRUEBA DEL GENERADOR DE COMPRAS
# -------------------------------------------------

from generador_compras import generar_compra

print("\n================================")
print("PRUEBA DEL GENERADOR DE COMPRAS")
print("================================")

resultado_compra = generar_compra(
    base_imponible=10000,
    igv=1800,
    total=11800,
    condicion_pago="CREDITO"
)

print("\nASIENTO GENERADO")

for cuenta in resultado_compra["cuentas"]:
    print(
        cuenta["codigo"],
        "-",
        cuenta["cuenta"],
        "| Debe:",
        cuenta["debe"],
        "| Haber:",
        cuenta["haber"]
    )

print("\nTOTAL DEBE:", resultado_compra["debe"])
print("TOTAL HABER:", resultado_compra["haber"])
print("DIFERENCIA:", resultado_compra["diferencia"])
print("¿ASIENTO CUADRADO?:", resultado_compra["cuadrado"])
# -------------------------------------------------
# PRUEBA VISUAL DEL GENERADOR DE COMPRAS
# -------------------------------------------------
st.divider()
st.subheader("🧾 Prueba del generador de compras")

if st.button("PROBAR GENERADOR DE COMPRA"):
    resultado_visual = generar_compra(
        base_imponible=10000,
        igv=1800,
        total=11800,
        condicion_pago="CREDITO"
    )

    st.write("### Asiento generado")
    for cuenta in resultado_visual["cuentas"]:
        st.write(
            cuenta["codigo"],
            "-",
            cuenta["cuenta"],
            "| Debe:",
            cuenta["debe"],
            "| Haber:",
            cuenta["haber"]
        )

    st.write("### Validación")
    st.write("Debe:", resultado_visual["debe"])
    st.write("Haber:", resultado_visual["haber"])
    st.write("Diferencia:", resultado_visual["diferencia"])

    if resultado_visual["cuadrado"]:
        st.success("✅ El asiento está cuadrado.")
    else:
        st.error("❌ El asiento NO está cuadrado.")
# -------------------------------------------------
# RESOLVER EJERCICIO CON IA
# -------------------------------------------------
from interpretador_gemini import extraer_datos_compra
from generador_excel import generar_excel_compra

st.divider()
st.subheader("📚 Resolver ejercicio con IA")

texto_ejercicio = st.text_area(
    "Pega aquí el enunciado del ejercicio de compra:",
    height=200
)

if st.button("RESOLVER CON IA"):
    if texto_ejercicio.strip() == "":
        st.warning("Por favor pega un ejercicio antes de continuar.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            with st.spinner("La IA está leyendo el ejercicio..."):
                datos_extraidos = extraer_datos_compra(
                    texto_ejercicio, api_key
                )

            st.write("### Datos identificados por la IA")
            st.json(datos_extraidos)

            resultado_ia = generar_compra(
                base_imponible=datos_extraidos["base_imponible"],
                igv=datos_extraidos["igv"],
                total=datos_extraidos["total"],
                condicion_pago=datos_extraidos["condicion_pago"]
            )

            st.write("### Asiento generado")
            for cuenta in resultado_ia["cuentas"]:
                st.write(
                    cuenta["codigo"],
                    "-",
                    cuenta["cuenta"],
                    "| Debe:",
                    cuenta["debe"],
                    "| Haber:",
                    cuenta["haber"]
                )

            st.write("### Validación")
            st.write("Debe:", resultado_ia["debe"])
            st.write("Haber:", resultado_ia["haber"])
            st.write("Diferencia:", resultado_ia["diferencia"])
            
            if resultado_ia["cuadrado"]:
                st.success("✅ El asiento está cuadrado.")
            else:
                st.error("❌ El asiento NO está cuadrado.")

            archivo_excel = generar_excel_compra(
                datos_extraidos, resultado_ia
            )

            st.download_button(
                label="📥 Descargar Excel",
                data=archivo_excel,
                file_name="ejercicio_resuelto.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
              
        except Exception as error:
            st.error(f"Ocurrió un error al resolver el ejercicio: {error}")
# -------------------------------------------------
# RESOLVER VENTA CON IA (PRUEBA)
# -------------------------------------------------
from generador_ventas import generar_venta
from interpretador_gemini import extraer_datos_venta

st.divider()
st.subheader("🧪 Resolver venta con IA (prueba)")

texto_venta = st.text_area(
    "Pega aquí el enunciado del ejercicio de venta:",
    height=200
)

if st.button("RESOLVER VENTA CON IA"):
    if texto_venta.strip() == "":
        st.warning("Por favor pega un ejercicio antes de continuar.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            with st.spinner("La IA está leyendo el ejercicio..."):
                datos_venta = extraer_datos_venta(texto_venta, api_key)

            st.write("### Datos identificados por la IA")
            st.json(datos_venta)

            resultado_venta = generar_venta(
                base_imponible=datos_venta["base_imponible"],
                igv=datos_venta["igv"],
                total=datos_venta["total"],
                condicion_cobro=datos_venta["condicion_cobro"]
            )

            st.write("### Asiento generado")
            for cuenta in resultado_venta["cuentas"]:
                st.write(
                    cuenta["codigo"], "-", cuenta["cuenta"],
                    "| Debe:", cuenta["debe"],
                    "| Haber:", cuenta["haber"]
                )

            if resultado_venta["cuadrado"]:
                st.success("✅ El asiento está cuadrado.")
            else:
                st.error("❌ El asiento NO está cuadrado.")

            archivo_excel_venta = generar_excel_compra(
                datos_venta, resultado_venta
            )

            st.download_button(
                label="📥 Descargar Excel",
                data=archivo_excel_venta,
                file_name="venta_resuelta.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="descarga_venta"
            )

        except Exception as error:
            st.error(f"Ocurrió un error al resolver la venta: {error}")
# -------------------------------------------------
# RESOLVER PRESTAMO FINANCIERO CON IA
# -------------------------------------------------
from generador_prestamos import generar_prestamo_desde_enunciado
from interpretador_gemini import extraer_datos_prestamo
from generador_excel import generar_excel_multiples_asientos

st.divider()
st.subheader("🏦 Resolver préstamo financiero con IA")

texto_prestamo = st.text_area(
    "Pega aquí el enunciado del ejercicio de préstamo:",
    height=200,
    key="texto_prestamo"
)

if st.button("RESOLVER PRESTAMO CON IA"):
    if texto_prestamo.strip() == "":
        st.warning("Por favor pega un ejercicio antes de continuar.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            with st.spinner("La IA está leyendo el ejercicio..."):
                datos_prestamo = extraer_datos_prestamo(texto_prestamo, api_key)

            st.write("### Datos identificados por la IA")
            st.json(datos_prestamo)

            resultado = generar_prestamo_desde_enunciado(
                texto_enunciado=texto_prestamo,
                monto_prestamo=datos_prestamo["monto_prestamo"],
                monto_interes=datos_prestamo["monto_interes"],
                entidad_financiera=datos_prestamo.get("entidad_financiera", ""),
                medio_pago=datos_prestamo.get("medio_pago", "TRANSFERENCIA"),
                modalidad_interes=datos_prestamo.get("modalidad_interes")
            )

            if resultado["requiere_aclaracion"]:
                st.warning(
                    "No se pudo determinar si el interés es "
                    "ADELANTADO o VENCIDO (mes a mes). "
                    + resultado["deteccion"]["observacion"]
                )
            else:
                st.info(
                    f"Modalidad de interés detectada: "
                    f"**{resultado['deteccion']['modalidad']}**"
                )

                for asiento in resultado["asientos"]:
                    st.write(f"### {asiento['tipo_asiento']}")
                    for cuenta in asiento["cuentas"]:
                        st.write(
                            cuenta["codigo"], "-", cuenta["cuenta"],
                            "| Debe:", cuenta["debe"],
                            "| Haber:", cuenta["haber"]
                        )
                    if asiento["validacion"]["cuadrado"]:
                        st.success("✅ Este asiento está cuadrado.")
                    else:
                        st.error("❌ Este asiento NO está cuadrado.")

                archivo_excel_prestamo = generar_excel_multiples_asientos(
                    datos_prestamo, resultado["asientos"]
                )

                st.download_button(
                    label="📥 Descargar Excel",
                    data=archivo_excel_prestamo,
                    file_name="prestamo_resuelto.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="descarga_prestamo"
                )

        except Exception as error:
            st.error(f"Ocurrió un error al resolver el préstamo: {error}")
# -------------------------------------------------
# PRUEBA DE NUEVOS MOTORES (SIN IA, DATOS FIJOS)
# -------------------------------------------------
from generador_planilla import generar_planilla
from generador_depreciacion import generar_depreciacion
from generador_provision import generar_provision

st.divider()
st.subheader("🧪 Prueba de nuevos motores (datos fijos)")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("PROBAR PLANILLA"):
        resultado_planilla = generar_planilla(
            sueldo_bruto=2000,
            destino="ADMINISTRACION"
        )
        st.write("### Planilla — Sueldo bruto S/ 2,000")
        for cuenta in resultado_planilla["cuentas"]:
            st.write(
                cuenta["asiento"], "|",
                cuenta["codigo"], "-", cuenta["cuenta"],
                "| Debe:", cuenta["debe"],
                "| Haber:", cuenta["haber"]
            )
        if resultado_planilla["cuadrado"]:
            st.success("✅ Cuadrado")
        else:
            st.error("❌ NO cuadrado")

with col2:
    if st.button("PROBAR DEPRECIACIÓN"):
        resultado_deprec = generar_depreciacion(
            valor_activo=12000,
            tipo_activo="MAQUINARIA",
            vida_util_anios=10,
            periodo="MENSUAL",
            destino="ADMINISTRACION"
        )
        st.write("### Depreciación — Maquinaria S/ 12,000, vida útil 10 años")
        for cuenta in resultado_deprec["cuentas"]:
            st.write(
                cuenta["asiento"], "|",
                cuenta["codigo"], "-", cuenta["cuenta"],
                "| Debe:", cuenta["debe"],
                "| Haber:", cuenta["haber"]
            )
        if resultado_deprec["cuadrado"]:
            st.success("✅ Cuadrado")
        else:
            st.error("❌ NO cuadrado")

with col3:
    if st.button("PROBAR PROVISIÓN"):
        resultado_provision = generar_provision(
            monto=3000,
            destino="ADMINISTRACION"
        )
        st.write("### Provisión — Cobranza dudosa S/ 3,000")
        for cuenta in resultado_provision["cuentas"]:
            st.write(
                cuenta["asiento"], "|",
                cuenta["codigo"], "-", cuenta["cuenta"],
                "| Debe:", cuenta["debe"],
                "| Haber:", cuenta["haber"]
            )
        if resultado_provision["cuadrado"]:
            st.success("✅ Cuadrado")
        else:
            st.error("❌ NO cuadrado")


# -------------------------------------------------
# RESOLVER PLANILLA CON IA (PRUEBA)
# -------------------------------------------------
from interpretador_gemini import extraer_datos_planilla, extraer_datos_depreciacion, extraer_datos_provision

st.divider()
st.subheader("🧾 Resolver planilla con IA")

texto_planilla = st.text_area(
    "Pega aquí el enunciado del ejercicio de planilla:",
    height=200,
    key="texto_planilla"
)

if st.button("RESOLVER PLANILLA CON IA"):
    if texto_planilla.strip() == "":
        st.warning("Por favor pega un ejercicio antes de continuar.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            with st.spinner("La IA está leyendo el ejercicio..."):
                datos_planilla_ia = extraer_datos_planilla(texto_planilla, api_key)

            st.write("### Datos identificados por la IA")
            st.json(datos_planilla_ia)

            resultado_planilla_ia = generar_planilla(
                sueldo_bruto=datos_planilla_ia["sueldo_bruto"],
                incluir_pago_trabajador=datos_planilla_ia.get("incluir_pago_trabajador", True),
                incluir_pago_sunat=datos_planilla_ia.get("incluir_pago_sunat", True),
                destino=datos_planilla_ia.get("destino", "ADMINISTRACION")
            )

            for cuenta in resultado_planilla_ia["cuentas"]:
                st.write(
                    cuenta["asiento"], "|",
                    cuenta["codigo"], "-", cuenta["cuenta"],
                    "| Debe:", cuenta["debe"],
                    "| Haber:", cuenta["haber"]
                )

            if resultado_planilla_ia["cuadrado"]:
                st.success("✅ El asiento está cuadrado.")
            else:
                st.error("❌ El asiento NO está cuadrado.")

        except Exception as error:
            st.error(f"Ocurrió un error al resolver la planilla: {error}")


# -------------------------------------------------
# RESOLVER DEPRECIACIÓN CON IA (PRUEBA)
# -------------------------------------------------
st.divider()
st.subheader("🏭 Resolver depreciación con IA")

texto_depreciacion = st.text_area(
    "Pega aquí el enunciado del ejercicio de depreciación:",
    height=200,
    key="texto_depreciacion"
)

if st.button("RESOLVER DEPRECIACIÓN CON IA"):
    if texto_depreciacion.strip() == "":
        st.warning("Por favor pega un ejercicio antes de continuar.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            with st.spinner("La IA está leyendo el ejercicio..."):
                datos_deprec_ia = extraer_datos_depreciacion(texto_depreciacion, api_key)

            st.write("### Datos identificados por la IA")
            st.json(datos_deprec_ia)

            resultado_deprec_ia = generar_depreciacion(
                valor_activo=datos_deprec_ia["valor_activo"],
                tipo_activo=datos_deprec_ia.get("tipo_activo", "MAQUINARIA"),
                vida_util_anios=datos_deprec_ia.get("vida_util_anios"),
                tasa_anual=datos_deprec_ia.get("tasa_anual"),
                periodo=datos_deprec_ia.get("periodo", "MENSUAL"),
                destino=datos_deprec_ia.get("destino", "ADMINISTRACION")
            )

            for cuenta in resultado_deprec_ia["cuentas"]:
                st.write(
                    cuenta["asiento"], "|",
                    cuenta["codigo"], "-", cuenta["cuenta"],
                    "| Debe:", cuenta["debe"],
                    "| Haber:", cuenta["haber"]
                )

            if resultado_deprec_ia["cuadrado"]:
                st.success("✅ El asiento está cuadrado.")
            else:
                st.error("❌ El asiento NO está cuadrado.")

        except Exception as error:
            st.error(f"Ocurrió un error al resolver la depreciación: {error}")


# -------------------------------------------------
# RESOLVER PROVISIÓN CON IA (PRUEBA)
# -------------------------------------------------
st.divider()
st.subheader("📉 Resolver provisión de cobranza dudosa con IA")

texto_provision = st.text_area(
    "Pega aquí el enunciado del ejercicio de provisión:",
    height=200,
    key="texto_provision"
)

if st.button("RESOLVER PROVISIÓN CON IA"):
    if texto_provision.strip() == "":
        st.warning("Por favor pega un ejercicio antes de continuar.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            with st.spinner("La IA está leyendo el ejercicio..."):
                datos_provision_ia = extraer_datos_provision(texto_provision, api_key)

            st.write("### Datos identificados por la IA")
            st.json(datos_provision_ia)

            resultado_provision_ia = generar_provision(
                monto=datos_provision_ia["monto"],
                destino=datos_provision_ia.get("destino", "ADMINISTRACION")
            )

            for cuenta in resultado_provision_ia["cuentas"]:
                st.write(
                    cuenta["asiento"], "|",
                    cuenta["codigo"], "-", cuenta["cuenta"],
                    "| Debe:", cuenta["debe"],
                    "| Haber:", cuenta["haber"]
                )

            if resultado_provision_ia["cuadrado"]:
                st.success("✅ El asiento está cuadrado.")
            else:
                st.error("❌ El asiento NO está cuadrado.")

        except Exception as error:
            st.error(f"Ocurrió un error al resolver la provisión: {error}")
# -------------------------------------------------
# RESOLVER CUALQUIER EJERCICIO CON IA (UNIFICADO)
# -------------------------------------------------
import re
from clasificador_gemini import clasificar_ejercicio


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


if "historial_asientos" not in st.session_state:
    st.session_state.historial_asientos = []

if "historial_resumen" not in st.session_state:
    st.session_state.historial_resumen = []

st.divider()
st.subheader("🎓 Resolver ejercicio(s) contable(s) con IA")

if st.session_state.historial_asientos:
    st.caption(
        f"📋 Llevas {len(st.session_state.historial_resumen)} ejercicio(s) "
        f"resuelto(s) en esta sesión. El Excel incluirá todos."
    )

texto_unificado = st.text_area(
    "Pega aquí uno o VARIOS ejercicios (numéralos como 1. 2. 3. si son "
    "varios): compra, venta, planilla, depreciación, provisión o préstamo.",
    height=220,
    key="texto_unificado"
)

col_resolver, col_limpiar = st.columns([3, 1])

with col_resolver:
    boton_resolver = st.button("RESOLVER EJERCICIO(S)")

with col_limpiar:
    if st.button("🗑️ Limpiar historial"):
        st.session_state.historial_asientos = []
        st.session_state.historial_resumen = []
        st.rerun()

if boton_resolver:
    if texto_unificado.strip() == "":
        st.warning("Por favor pega al menos un ejercicio antes de continuar.")
    else:
        api_key = st.secrets["GEMINI_API_KEY"]
        lista_ejercicios = _dividir_ejercicios(texto_unificado)

        st.caption(f"Se detectaron {len(lista_ejercicios)} ejercicio(s) en el texto pegado.")

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

                numero_global = len(st.session_state.historial_resumen) + 1
                st.session_state.historial_asientos.extend(asientos_finales)
                st.session_state.historial_resumen.append({
                    f"Ejercicio {numero_global} - Tipo": tipo_detectado,
                    f"Ejercicio {numero_global} - Datos": str(datos_generales)
                })

            except Exception as error:
                st.error(f"Ocurrió un error al resolver el ejercicio {indice_ejercicio}: {error}")

        st.success(
            f"Listo. Van {len(st.session_state.historial_resumen)} ejercicio(s) "
            f"en el historial de esta sesión."
        )

# -------------------------------------------------
# DESCARGA DEL EXCEL ACUMULADO (TODOS LOS EJERCICIOS)
# -------------------------------------------------
if st.session_state.historial_asientos:
    resumen_acumulado = {}
    for entrada in st.session_state.historial_resumen:
        resumen_acumulado.update(entrada)

    archivo_excel_unificado = generar_excel_multiples_asientos(
        resumen_acumulado, st.session_state.historial_asientos
    )

    st.download_button(
        label=f"📥 Descargar Excel completo ({len(st.session_state.historial_resumen)} ejercicio(s))",
        data=archivo_excel_unificado,
        file_name="ejercicios_resueltos.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="descarga_unificado"
    )
