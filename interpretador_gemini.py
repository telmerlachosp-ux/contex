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

def extraer_datos_venta(texto_ejercicio, api_key):
    """
    Recibe el texto de un ejercicio de venta y le pide a Gemini
    que extraiga los datos necesarios en formato JSON.
    """
    cliente = genai.Client(api_key=api_key)

    prompt = f"""
Eres un asistente contable. Lee el siguiente ejercicio y extrae ÚNICAMENTE
los datos numéricos necesarios para registrar una VENTA.

Responde EXCLUSIVAMENTE con un objeto JSON válido, sin explicaciones,
sin texto adicional, sin marcas de código (nada de ```).

El formato exacto debe ser:
{{
  "base_imponible": numero,
  "igv": numero,
  "total": numero,
  "condicion_cobro": "CREDITO" o "CONTADO",
  "medio_pago": "EFECTIVO" o "TRANSFERENCIA"
}}

Reglas:
- Si el ejercicio no da el IGV directamente, calcúlalo con 18% sobre la base.
- Si no da el total, calcúlalo sumando base + igv.
- "medio_pago" solo importa si condicion_cobro es "CONTADO": usa
  "EFECTIVO" si se pagó en efectivo/caja, o "TRANSFERENCIA" si fue
  transferencia, depósito, cheque o tarjeta. Si es "CREDITO" o no
  se especifica, usa "EFECTIVO" por defecto.

Ejercicio:
\"\"\"{texto_ejercicio}\"\"\"
"""

    interaction = cliente.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    texto_respuesta = interaction.output_text
    texto_limpio = re.sub(r"```json|```", "", texto_respuesta).strip()

    datos = json.loads(texto_limpio)

    return datos

def extraer_datos_prestamo(texto_ejercicio, api_key):
    """
    Recibe el texto de un ejercicio de préstamo financiero y le pide
    a Gemini que extraiga los datos necesarios en formato JSON.
    """
    cliente = genai.Client(api_key=api_key)

    prompt = f"""
Eres un asistente contable. Lee el siguiente ejercicio y extrae ÚNICAMENTE
los datos numéricos necesarios para registrar un PRÉSTAMO FINANCIERO.

Responde EXCLUSIVAMENTE con un objeto JSON válido, sin explicaciones,
sin texto adicional, sin marcas de código (nada de ```).

El formato exacto debe ser:
{{
  "monto_prestamo": numero,
  "monto_interes": numero,
  "entidad_financiera": "nombre del banco o entidad, o vacío si no se menciona",
  "medio_pago": "EFECTIVO" o "TRANSFERENCIA",
  "modalidad_interes": "ADELANTADO" o "VENCIDO"
}}

Reglas:
- Si el enunciado menciona que el interés se paga "por adelantado",
  "anticipado" o "se descuenta", usa "ADELANTADO".
- Si el enunciado menciona "mes a mes", "mensualmente" o "al vencimiento",
  usa "VENCIDO".
- Si no queda claro, usa "VENCIDO" (es lo más común).
- Si no se menciona el medio de pago, usa "TRANSFERENCIA".

Ejercicio:
\"\"\"{texto_ejercicio}\"\"\"
"""

    interaction = cliente.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    texto_respuesta = interaction.output_text
    texto_limpio = re.sub(r"```json|```", "", texto_respuesta).strip()

    datos = json.loads(texto_limpio)

    return datos


def extraer_datos_planilla(texto_ejercicio, api_key):
    """
    Recibe el texto de un ejercicio de planilla y le pide a Gemini
    que extraiga los datos necesarios en formato JSON.
    """
    cliente = genai.Client(api_key=api_key)

    prompt = f"""
Eres un asistente contable. Lee el siguiente ejercicio y extrae ÚNICAMENTE
los datos numéricos necesarios para registrar una PLANILLA DE SUELDOS.

Responde EXCLUSIVAMENTE con un objeto JSON válido, sin explicaciones,
sin texto adicional, sin marcas de código (nada de ```).

El formato exacto debe ser:
{{
  "sueldo_bruto": numero,
  "incluir_pago_trabajador": true o false,
  "incluir_pago_sunat": true o false,
  "destino": "ADMINISTRACION" o "VENTAS"
}}

Reglas:
- "sueldo_bruto" es el sueldo antes de descuentos (ONP y Essalud se
  calculan automáticamente con las tasas estándar: ONP 13%, Essalud 9%).
- "incluir_pago_trabajador" es true si el enunciado menciona que se pagó
  o se debe pagar el sueldo al trabajador; si el enunciado solo pide la
  provisión, usa false.
- "incluir_pago_sunat" es true si el enunciado menciona el pago de los
  aportes (ONP/Essalud) a SUNAT; si no lo menciona, usa false.
- "destino" es "VENTAS" si el trabajador es vendedor, de ventas o
  comercial; en cualquier otro caso (o si no se especifica), usa
  "ADMINISTRACION".

Ejercicio:
\"\"\"{texto_ejercicio}\"\"\"
"""

    interaction = cliente.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    texto_respuesta = interaction.output_text
    texto_limpio = re.sub(r"```json|```", "", texto_respuesta).strip()

    datos = json.loads(texto_limpio)

    return datos


def extraer_datos_depreciacion(texto_ejercicio, api_key):
    """
    Recibe el texto de un ejercicio de depreciación y le pide a Gemini
    que extraiga los datos necesarios en formato JSON.
    """
    cliente = genai.Client(api_key=api_key)

    prompt = f"""
Eres un asistente contable. Lee el siguiente ejercicio y extrae ÚNICAMENTE
los datos numéricos necesarios para calcular la DEPRECIACIÓN de un activo fijo.

Responde EXCLUSIVAMENTE con un objeto JSON válido, sin explicaciones,
sin texto adicional, sin marcas de código (nada de ```).

El formato exacto debe ser:
{{
  "valor_activo": numero,
  "tipo_activo": "EDIFICACION" o "MAQUINARIA" o "VEHICULO" o "MUEBLES" o "EQUIPO_DIVERSO",
  "vida_util_anios": numero o null,
  "tasa_anual": numero o null,
  "periodo": "MENSUAL" o "ANUAL",
  "destino": "ADMINISTRACION" o "VENTAS"
}}

Reglas:
- "tipo_activo" se identifica según el activo mencionado: edificios/locales
  -> "EDIFICACION"; maquinaria/equipos de producción -> "MAQUINARIA";
  vehículos/camiones/autos -> "VEHICULO"; muebles/escritorios/sillas ->
  "MUEBLES"; computadoras/equipos de cómputo/equipos diversos ->
  "EQUIPO_DIVERSO". Si no queda claro, usa "MAQUINARIA".
- Si el enunciado da la VIDA ÚTIL en años (ej. "10 años"), pon ese número
  en "vida_util_anios" y deja "tasa_anual" en null.
- Si el enunciado da la TASA directamente (ej. "10% anual"), pon ese
  número (como decimal, ej. 0.10) en "tasa_anual" y deja
  "vida_util_anios" en null.
- Si no especifica el período, usa "MENSUAL" (el más común).
- "destino" es "VENTAS" si el activo se usa para vender o repartir
  (ej. vehículo de reparto); en cualquier otro caso, usa "ADMINISTRACION".

Ejercicio:
\"\"\"{texto_ejercicio}\"\"\"
"""

    interaction = cliente.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    texto_respuesta = interaction.output_text
    texto_limpio = re.sub(r"```json|```", "", texto_respuesta).strip()

    datos = json.loads(texto_limpio)

    return datos


def extraer_datos_provision(texto_ejercicio, api_key):
    """
    Recibe el texto de un ejercicio de provisión de cobranza dudosa
    y le pide a Gemini que extraiga los datos necesarios en formato JSON.
    """
    cliente = genai.Client(api_key=api_key)

    prompt = f"""
Eres un asistente contable. Lee el siguiente ejercicio y extrae ÚNICAMENTE
los datos numéricos necesarios para registrar una PROVISIÓN (ESTIMACIÓN)
DE COBRANZA DUDOSA.

Responde EXCLUSIVAMENTE con un objeto JSON válido, sin explicaciones,
sin texto adicional, sin marcas de código (nada de ```).

El formato exacto debe ser:
{{
  "monto": numero,
  "destino": "ADMINISTRACION" o "VENTAS"
}}

Reglas:
- "monto" es el importe de la cuenta por cobrar que se estima incobrable.
- "destino" es "VENTAS" si el enunciado lo relaciona con el área de
  ventas; en cualquier otro caso (o si no se especifica), usa
  "ADMINISTRACION".

Ejercicio:
\"\"\"{texto_ejercicio}\"\"\"
"""

    interaction = cliente.interactions.create(
        model="gemini-3.5-flash-lite",
        input=prompt
    )

    texto_respuesta = interaction.output_text
    texto_limpio = re.sub(r"```json|```", "", texto_respuesta).strip()

    datos = json.loads(texto_limpio)

    return datos
