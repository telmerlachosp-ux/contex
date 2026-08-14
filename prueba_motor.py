from motor_reglas import generar_asiento_compra


# ==========================================
# PRUEBA DE COMPRA AL CRÉDITO
# ==========================================

resultado = generar_asiento_compra(
    base_imponible=10000,
    igv=1800,
    total=11800,
    condicion_pago="CREDITO"
)


print("==========================================")
print("PRUEBA DE GENERADOR DE COMPRA")
print("==========================================")

print()

print("ASIENTO CONTABLE")

print()

for cuenta in resultado["cuentas"]:

    print(
        cuenta["codigo"],
        "-",
        cuenta["cuenta"]
    )

    print(
        "Debe:",
        cuenta["debe"],
        "| Haber:",
        cuenta["haber"]
    )

    print()


print("==========================================")
print("VALIDACIÓN")
print("==========================================")

print(
    "Debe:",
    resultado["validacion"]["debe"]
)

print(
    "Haber:",
    resultado["validacion"]["haber"]
)

print(
    "Diferencia:",
    resultado["validacion"]["diferencia"]
)

print(
    "¿Está cuadrado?:",
    resultado["validacion"]["cuadrado"]
)
