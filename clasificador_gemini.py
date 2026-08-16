import re
from google import genai

TIPOS_VALIDOS = {
    "COMPRA",
    "VENTA",
    "PLANILLA",
    "DEPRECIACION",
    "PROVISION",
    "PRESTAMO"
}

_PALABRAS_CLAVE = {
    "COMPRA": ["compra de", "compró", "adquiere", "adquirió", "adquisición"],
    "VENTA": ["vende", "venta de", "vendió"],
    "PLANILLA": ["sueldo", "planilla", "remuneracion", "remuneración", "trabajador", "empleado"],
    "DEPRECIACION": ["deprecia"],
    "PROVISION": ["cobranza dudosa", "incobrable", "estimación de cobranza"],
    "PRESTAMO": ["préstamo", "prestamo", "financiamiento", "entidad financiera"],
}


def _clasificar_por_palabras_clave(texto_ejercicio):
    """
    Intenta identificar el tipo de ejercicio usando palabras clave,
    sin llamar a la IA. Busca cada palabra como PALABRA COMPLETA
    (con límites de palabra), para que "vende" no dispare dentro
    de "vendedor", por ejemplo.

    Devuelve el tipo si hay una única coincidencia clara, o None
    si es ambiguo (0 o más de 1 tipo coincide).
    """
    texto = texto_ejercicio.lower()

    tipos_encontrados = []
    for tipo, palabras in _PALABRAS_CLAVE.items():
        for palabra in palabras:
            patron = r"\b" + re.escape(palabra) + r"\b"
            if re.search(patron, texto):
                tipos_encontrados.append(tipo)
                break

    if len(tipos_encontrados) == 1:
        return tipos_encontrados[0]

    return None


def clasificar_ejercicio(texto_ejercicio, api_key):
    """
    Determina qué tipo de operación es el ejercicio.
    Primero intenta con palabras clave (rápido y confiable para
    ejercicios básicos); si es ambiguo, le pregunta a Gemini.

    Devuelve un string: "COMPRA", "VENTA", "PLANILLA",
    "DEPRECIACION", "PROVISION" o "PRESTAMO".
    """
    tipo_por_palabras = _clasificar_por_palabras_clave(texto_ejercicio)
    if tipo_por_palabras:
        return tipo_por_palabras

    cliente = genai.Client(api_key=api_key)

    prompt = f"""
Eres un asistente contable. Lee el siguiente ejercicio y determina
a cuál de estas categorías pertenece:

- COMPRA: adquisición de mercadería o bienes para la empresa.
- VENTA: venta de mercadería o bienes a un cliente.
- PLANILLA: pago o provisión de sueldos a trabajadores.
- DEPRECIACION: depreciación de un activo fijo (maquinaria,
  edificio, vehículo, muebles, equipo).
- PROVISION: estimación o provisión de cobranza dudosa sobre
  cuentas por cobrar.
- PRESTAMO: obtención de un préstamo o financiamiento de una
  entidad financiera (banco).

Responde EXCLUSIVAMENTE con una sola palabra, en mayúsculas, sin
explicaciones ni texto adicional: COMPRA, VENTA, PLANILLA,
DEPRECIACION, PROVISION o PRESTAMO.

Ejercicio:
\"\"\"{texto_ejercicio}\"\"\"
"""

    interaction = cliente.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    texto_respuesta = interaction.output_text
    tipo = re.sub(r"[^A-ZÁÉÍÓÚ]", "", texto_respuesta.strip().upper())
    tipo = tipo.replace("Ó", "O")

    if tipo not in TIPOS_VALIDOS:
        raise ValueError(
            f"No se pudo identificar el tipo de ejercicio (la IA respondió: '{texto_respuesta.strip()}')."
        )

    return tipo
