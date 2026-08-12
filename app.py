import streamlit as st

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
    "Selecciona tu archivo",
    type=["pdf", "docx", "jpg", "jpeg", "png"]
)

if archivo is not None:
    st.success(f"Archivo cargado: {archivo.name}")

    if st.button("PROCESAR"):
        st.info("CONTEX está listo para procesar tu documento.")
