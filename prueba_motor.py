from motor_reglas import (
    determinar_igv,
    verificar_bancarizacion,
    validar_asiento
)


print("====================================")
print("      PRUEBA DEL MOTOR DE CONTEX")
print("====================================")


# ------------------------------------
# 1. PRUEBA DEL IGV
# ------------------------------------

print("\n1. PRUEBA DEL IGV")

resultado_igv = determinar_igv(
    tratamiento_igv="GRAVADA",
    base_imponible=10000
)

print("Base:", resultado_igv["base_imponible"])
print("IGV:", resultado_igv["igv"])
print("Total:", resultado_igv["total"])


# ------------------------------------
# 2. PRUEBA DE BANCARIZACIÓN
# ------------------------------------

print("\n2. PRUEBA DE BANCARIZACIÓN")

resultado_bancarizacion = verificar_bancarizacion(
    monto_pago=5000,
    medio_pago=None
)

print(
    "Bancarización obligatoria:",
    resultado_bancarizacion["bancarizacion_obligatoria"]
)

print(
    "Medio de pago:",
    resultado_bancarizacion["medio_pago"]
)

print(
    "Observación:",
    resultado_bancarizacion["observacion"]
)


# ------------------------------------
# 3. PRUEBA DE ASIENTO
# ------------------------------------

print("\n3. PRUEBA DE VALIDACIÓN")

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


resultado_validacion = validar_asiento(cuentas)

print("Debe:", resultado_validacion["debe"])
print("Haber:", resultado_validacion["haber"])
print("Diferencia:", resultado_validacion["diferencia"])
print("¿Está cuadrado?:", resultado_validacion["cuadrado"])


print("\n====================================")
print("       FIN DE LA PRUEBA")
print("====================================")
