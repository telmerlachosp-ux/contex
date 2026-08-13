import streamlit as st
import fitz


st.set_page_config(
    page_title="CONTEX",
    page_icon="📚",
    layout="centered"
)


st.title("CONTEX")
st.subheader("Asistente contable con inteligencia artificial")

st.write(
    "Sube una monografía o ejercicio contable "
    "y CONTEX analizará su contenido."
)


archivo = st.file_uploader(
    "Selecciona tu archivo PDF",
    type=["pdf"]
)


if archivo is not None:

    st.success(f"Archivo cargado: {archivo.name}")

    if st.button("LEER DOCUMENTO"):

        try:
            documento = fitz.open(stream=archivo.read(), filetype="pdf")

            texto_completo = ""

            for numero_pagina, pagina in enumerate(documento, start=1):

                texto_pagina = pagina.get_text()

                texto_completo += (
                    f"\n\n--- PÁGINA {numero_pagina} ---\n\n"
                    + texto_pagina
                )

            documento.close()

            if texto_completo.strip():

                st.success("Documento leído correctamente.")

                st.subheader("Texto extraído del documento")

                st.text_area(
                    "Contenido detectado:",
                    texto_completo,
                    height=500
                )

            else:

                st.warning(
                    "CONTEX no encontró texto digital en este PDF. "
                    "Es posible que el documento sea una imagen escaneada."
                )

        except Exception as error:

            st.error(
                f"No se pudo leer el documento: {error}"
            )
