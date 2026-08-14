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
