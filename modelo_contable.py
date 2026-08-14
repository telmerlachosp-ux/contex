from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class OperacionContable:

    # =========================
    # DATOS GENERALES
    # =========================

    numero: int = 0
    fecha: str = ""
    tipo: str = ""

    documento: str = ""
    numero_documento: str = ""
    descripcion: str = ""

    # =========================
    # CONDICIONES DE LA OPERACIÓN
    # =========================

    condicion_pago: str = ""
    medio_pago: Optional[str] = None
    moneda: str = "PEN"

    # =========================
    # INFORMACIÓN DEL IGV
    # =========================

    gravada_igv: Optional[bool] = None
    tratamiento_igv: str = ""
    tasa_igv: float = 0.0

    # =========================
    # IMPORTES
    # =========================

    base_imponible: float = 0.0
    igv: float = 0.0
    total: float = 0.0

    # =========================
    # BANCARIZACIÓN
    # =========================

    monto_pago: float = 0.0
    bancarizacion_obligatoria: bool = False
    observacion_tributaria: str = ""

    # =========================
    # CUENTAS CONTABLES
    # =========================

    cuentas: List[dict] = field(default_factory=list)


# ==========================================
# CREAR Y VALIDAR ASIENTO
# ==========================================

def crear_asiento(cuentas):

    """
    Crea y valida un asiento contable.
    """

    debe = sum(
        cuenta["debe"]
        for cuenta in cuentas
    )

    haber = sum(
        cuenta["haber"]
        for cuenta in cuentas
    )

    diferencia = round(
        debe - haber,
        2
    )

    return {
        "cuentas": cuentas,
        "debe": debe,
        "haber": haber,
        "diferencia": diferencia,
        "cuadrado": diferencia == 0
    }
