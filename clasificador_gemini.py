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


def clasificar_ejercicio(texto_ejercicio, api_key):
    """
    Lee el enunciado de un ejercicio contable y determina
    qué tipo de operación es, para poder mandarlo al motor
    correcto de forma automática.

    Devuelve un string: "COMPRA", "VENTA", "PLANILLA",
    "DEPRECIACION", "PROVISION" o "PRESTAMO".
    """
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
