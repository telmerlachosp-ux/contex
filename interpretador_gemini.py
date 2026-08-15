import json
import re
from google import genai


def extraer_datos_compra(texto_ejercicio, api_key):
    """
    Recibe el texto de un ejercicio de compra y le pide a Gemini
    que extraiga los datos necesarios en formato JSON.
    """
    cliente = genai.Client(api_key=api_key)

    prompt = f"""
Eres un asistente contable. Lee el siguiente ejercicio y extrae ÚNICAMENTE
los datos numéricos necesarios para registrar una COMPRA.

Responde EXCLUSIVAMENTE con un objeto JSON válido, sin explicaciones,
sin texto adicional, sin marcas de código (nada de ```).

El formato exacto debe ser:
{{
  "base_imponible": numero,
  "igv": numero,
  "total": numero,
  "condicion_pago": "CREDITO" o "CONTADO"
}}

Si el ejercicio no da el IGV directamente, calcúlalo con 18% sobre la base.
Si no da el total, calcúlalo sumando base + igv.

Ejercicio:
\"\"\"{texto_ejercicio}\"\"\"
"""

    interaction = cliente.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    texto_respuesta = interaction.output_text

    # Por seguridad, limpiamos posibles restos de ```json ... ```
    texto_limpio = re.sub(r"```json|```", "", texto_respuesta).strip()

    datos = json.loads(texto_limpio)

    return datos
