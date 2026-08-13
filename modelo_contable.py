from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class OperacionContable:
    numero: int = 0
    fecha: str = ""
    tipo: str = ""
    documento: str = ""
    numero_documento: str = ""
    descripcion: str = ""

    condicion_pago: str = ""
    medio_pago: Optional[str] = None

    moneda: str = "PEN"
    base_imponible: float = 0.0
    igv: float = 0.0
    total: float = 0.0

    monto_pago: float = 0.0
    bancarizacion_obligatoria: bool = False
    observacion_tributaria: str = ""

    cuentas: List[dict] = field(default_factory=list)
