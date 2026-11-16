"""Interpolación lineal propia sobre el dominio validado de la bomba."""

import math
from itertools import pairwise

from pumpcalc.entradas import CurvaBomba, ErrorEntrada, PuntoBomba


def altura_bomba(curva: CurvaBomba, caudal_m3s: float) -> float:
    """Devuelve H en metros para Q en m³/s."""
    altura, _ = interpolar_bomba(curva, caudal_m3s)
    return altura


def interpolar_bomba(
    curva: CurvaBomba, caudal_m3s: float
) -> tuple[float, tuple[PuntoBomba, PuntoBomba]]:
    """Devuelve la altura y el tramo que la explica dentro de la curva."""
    minimo, maximo = curva.dominio_m3s
    if not math.isfinite(caudal_m3s) or not minimo <= caudal_m3s <= maximo:
        raise ErrorEntrada('caudal_m3s', 'El caudal debe estar dentro del dominio de la curva.')
    # En un nodo compartido se usa el tramo anterior y se conserva su altura exacta.
    for izquierdo, derecho in pairwise(curva.puntos):
        if caudal_m3s > derecho.caudal_m3s:
            continue
        tramo = (izquierdo, derecho)
        if caudal_m3s == izquierdo.caudal_m3s:
            return izquierdo.altura_m, tramo
        if caudal_m3s == derecho.caudal_m3s:
            return derecho.altura_m, tramo
        fraccion = (
            (caudal_m3s - izquierdo.caudal_m3s)
            / (derecho.caudal_m3s - izquierdo.caudal_m3s)
        )
        altura = izquierdo.altura_m + fraccion * (derecho.altura_m - izquierdo.altura_m)
        return altura, tramo
    raise RuntimeError('La curva validada no contiene un tramo para este caudal.')
