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
# ENCABEZADO
# ==========================================

st.title("CONTEX")
st.subheader("Asistente contable con inteligencia artificial")

st.write(
    "Sube una monografía o ejercicio contable "
    "y CONTEX analizará su contenido."
)


# ==========================================
# CARGA DEL PDF
# ==========================================

archivo = st.file_uploader(
    "Selecciona tu archivo PDF",
    type=["pdf"]
)


if archivo is not None:

    st.success(f"Archivo cargado: {archivo.name}")

    if st.button("LEER DOCUMENTO"):

        try:

            documento = fitz.open(
                stream=archivo.read(),
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

            if texto_completo.strip():

                st.success(
                    "Documento leído correctamente."
                )

                st.subheader(
                    "Texto extraído del documento"
                )

                st.text_area(
                    "Contenido detectado:",
                    texto_completo,
                    height=500
                )

            else:

                st.warning(
                    "CONTEX no encontró texto digital "
                    "en este PDF. Es posible que el "
                    "documento sea una imagen escaneada."
                )

        except Exception as error:

            st.error(
                f"No se pudo leer el documento: {error}"
            )


# ==========================================
# PRUEBA DEL MOTOR CONTABLE
# ==========================================

st.divider()

st.subheader("🧪 Prueba del motor de CONTEX")


if st.button("PROBAR MOTOR"):

    # --------------------------------------
    # PRUEBA DEL IGV
    # --------------------------------------

    resultado_igv = determinar_igv(
        tratamiento_igv="GRAVADA",
        base_imponible=10000
    )


    # --------------------------------------
    # PRUEBA DE BANCARIZACIÓN
    # --------------------------------------

    resultado_bancarizacion = verificar_bancarizacion(
        monto_pago=5000,
        medio_pago=None
    )


    # --------------------------------------
    # CUENTAS DEL ASIENTO
    # --------------------------------------

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


    # --------------------------------------
    # VALIDACIÓN
    # --------------------------------------

    resultado_validacion = validar_asiento(
        cuentas
    )


    # --------------------------------------
    # MOSTRAR RESULTADOS DEL IGV
    # --------------------------------------

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


    # --------------------------------------
    # MOSTRAR BANCARIZACIÓN
    # --------------------------------------

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


    # --------------------------------------
    # MOSTRAR VALIDACIÓN
    # --------------------------------------

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
