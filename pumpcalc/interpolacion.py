"""Interpolación lineal propia sobre el dominio validado de la bomba."""

import math

from pumpcalc.entradas import CurvaBomba, ErrorEntrada


def altura_bomba(curva: CurvaBomba, caudal_m3s: float) -> float:
    """Devuelve H en metros para Q en m³/s, sin extrapolar ni redondear."""
    minimo, maximo = curva.dominio_m3s
    if not math.isfinite(caudal_m3s) or not minimo <= caudal_m3s <= maximo:
        raise ErrorEntrada('caudal_m3s', 'El caudal debe estar dentro del dominio de la curva.')
    for punto in curva.puntos:
        if caudal_m3s == punto.caudal_m3s:
            return punto.altura_m
    for izquierdo, derecho in zip(curva.puntos, curva.puntos[1:]):
        if izquierdo.caudal_m3s < caudal_m3s < derecho.caudal_m3s:
            fraccion = ((caudal_m3s - izquierdo.caudal_m3s)
                        / (derecho.caudal_m3s - izquierdo.caudal_m3s))
            return izquierdo.altura_m + fraccion * (derecho.altura_m - izquierdo.altura_m)
    raise RuntimeError('La curva validada no contiene un tramo para este caudal.')
