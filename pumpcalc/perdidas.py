"""Altura de la instalación por Darcy–Weisbach y K total, en unidades SI."""

from dataclasses import dataclass
import math

from pumpcalc.entradas import ErrorEntrada, Instalacion
from pumpcalc.friccion import (
    MAX_ITERACIONES_COLEBROOK, ResultadoFriccion, factor_friccion,
)


GRAVEDAD = 9.81  # m/s²
VISCOSIDAD_CINEMATICA = 1.004e-6  # m²/s, agua a aproximadamente 20 °C


@dataclass(frozen=True)
class ResultadoSistema:
    caudal_m3s: float
    area_m2: float
    velocidad_ms: float
    reynolds: float
    perdida_tuberia_m: float
    perdida_accesorios_m: float
    altura_sistema_m: float
    friccion: ResultadoFriccion


def evaluar_sistema(instalacion: Instalacion, caudal_m3s: float, *,
                    max_iteraciones_colebrook: int = MAX_ITERACIONES_COLEBROOK) -> ResultadoSistema:
    """Evalúa Hs(Q); los fallos de Colebrook se propagan sin sustituir f."""
    if not math.isfinite(caudal_m3s) or not 0 <= caudal_m3s <= 100 / 3600:
        raise ErrorEntrada('caudal_m3s', 'El caudal debe estar entre 0 y 100/3600 m³/s.')
    area = math.pi * instalacion.diametro_m ** 2 / 4
    if caudal_m3s == 0:
        # No se evalúa ni 64/Re ni Colebrook: f es no aplicable.
        return ResultadoSistema(
            0, area, 0, 0, 0, 0, instalacion.desnivel_m,
            ResultadoFriccion(None, 'sin_flujo'),
        )
    velocidad = caudal_m3s / area
    reynolds = velocidad * instalacion.diametro_m / VISCOSIDAD_CINEMATICA
    friccion = factor_friccion(
        reynolds, instalacion.rugosidad_m / instalacion.diametro_m,
        max_iteraciones=max_iteraciones_colebrook,
    )
    altura_velocidad = velocidad ** 2 / (2 * GRAVEDAD)
    # Ambos términos son alturas de energía en metros, igual que el desnivel.
    perdida_tuberia = (
        friccion.factor_darcy * instalacion.longitud_m
        / instalacion.diametro_m * altura_velocidad
    )
    perdida_accesorios = instalacion.k_total * altura_velocidad
    return ResultadoSistema(
        caudal_m3s, area, velocidad, reynolds, perdida_tuberia, perdida_accesorios,
        instalacion.desnivel_m + perdida_tuberia + perdida_accesorios, friccion,
    )
