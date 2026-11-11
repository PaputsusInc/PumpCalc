"""Datos y validación de la línea base vigente, independientes de NiceGUI.

Las entradas visibles usan mm y m³/h; los objetos del motor usan m y m³/s.
La meta se valida aparte porque es común a los escenarios A y B.
"""

from collections.abc import Sequence
from dataclasses import dataclass
import math
import re


class ErrorEntrada(ValueError):
    """Error que permite señalar el campo o la celda que debe corregirse."""

    def __init__(self, campo: str, mensaje: str) -> None:
        self.campo = campo
        super().__init__(mensaje)


def numero_decimal(valor: object, campo: str) -> float:
    """Acepta punto o coma decimal, sin separadores de miles ni vacíos."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        raise ErrorEntrada(campo, 'Este campo es obligatorio.')
    if isinstance(valor, bool) or not isinstance(valor, (str, int, float)):
        raise ErrorEntrada(campo, 'Introduce un número válido.')
    if isinstance(valor, str):
        texto = valor.strip()
        if not re.fullmatch(r'[+-]?(?:[0-9]+(?:[.,][0-9]*)?|[.,][0-9]+)(?:[eE][+-]?[0-9]+)?', texto):
            raise ErrorEntrada(campo, 'Usa coma o punto decimal, sin separadores de miles.')
        valor = texto.replace(',', '.')
    try:
        numero = float(valor)
    except (ValueError, OverflowError):
        raise ErrorEntrada(campo, 'Introduce un número finito.') from None
    if not math.isfinite(numero):
        raise ErrorEntrada(campo, 'Introduce un número finito.')
    return numero


def _rango(valor: float, minimo: float, maximo: float, campo: str,
           *, positivo: bool = False) -> None:
    if not math.isfinite(valor) or not minimo <= valor <= maximo or (positivo and valor == 0):
        limite = f'mayor que {minimo:g}' if positivo else f'mayor o igual a {minimo:g}'
        raise ErrorEntrada(campo, f'Debe ser finito, {limite} y menor o igual a {maximo:g}.')


@dataclass(frozen=True)
class Instalacion:
    """Instalación validada en unidades del motor: metros y K sin unidad."""

    longitud_m: float
    diametro_m: float
    desnivel_m: float
    rugosidad_m: float
    k_total: float

    def __post_init__(self) -> None:
        _rango(self.longitud_m, 0, 1000, 'longitud_m', positivo=True)
        _rango(self.diametro_m, 0.01, 0.2, 'diametro_m')
        _rango(self.desnivel_m, 0, 100, 'desnivel_m')
        _rango(self.rugosidad_m, 0, 0.001, 'rugosidad_m')
        _rango(self.k_total, 0, 100, 'k_total')
        if self.longitud_m < self.desnivel_m:
            raise ErrorEntrada('longitud_m', 'La longitud debe ser mayor o igual al desnivel.')
        if self.rugosidad_m / self.diametro_m > 0.05:
            raise ErrorEntrada('rugosidad_m', 'La rugosidad relativa ε/D no puede superar 0,05.')


@dataclass(frozen=True)
class PuntoBomba:
    caudal_m3s: float
    altura_m: float

    def __post_init__(self) -> None:
        _rango(self.caudal_m3s, 0, 100 / 3600, 'caudal_m3s')
        _rango(self.altura_m, 0, 200, 'altura_m')


@dataclass(frozen=True)
class CurvaBomba:
    puntos: tuple[PuntoBomba, ...]

    def __post_init__(self) -> None:
        # Una tupla evita que editar la lista original altere una curva validada.
        object.__setattr__(self, 'puntos', tuple(self.puntos))
        if not 3 <= len(self.puntos) <= 10:
            raise ErrorEntrada('puntos', 'Introduce entre 3 y 10 puntos de bomba.')
        for indice, (anterior, actual) in enumerate(zip(self.puntos, self.puntos[1:]), 2):
            if actual.caudal_m3s <= anterior.caudal_m3s:
                raise ErrorEntrada(f'puntos.{indice}.caudal_m3h',
                                   'Los caudales deben ser estrictamente crecientes, sin duplicados.')
            if actual.altura_m > anterior.altura_m:
                raise ErrorEntrada(f'puntos.{indice}.altura_m',
                                   'Las alturas deben ser no crecientes.')

    @property
    def dominio_m3s(self) -> tuple[float, float]:
        return self.puntos[0].caudal_m3s, self.puntos[-1].caudal_m3s


@dataclass(frozen=True)
class Escenario:
    instalacion: Instalacion
    curva: CurvaBomba


def validar_instalacion(*, longitud_m: object, diametro_mm: object,
                       desnivel_m: object, rugosidad_mm: object,
                       k_total: object) -> Instalacion:
    """Valida las entradas visibles y convierte milímetros a metros."""
    longitud = numero_decimal(longitud_m, 'longitud_m')
    diametro = numero_decimal(diametro_mm, 'diametro_mm')
    desnivel = numero_decimal(desnivel_m, 'desnivel_m')
    rugosidad = numero_decimal(rugosidad_mm, 'rugosidad_mm')
    k = numero_decimal(k_total, 'k_total')
    _rango(diametro, 10, 200, 'diametro_mm')
    _rango(rugosidad, 0, 1, 'rugosidad_mm')
    if rugosidad / diametro > 0.05:
        raise ErrorEntrada('rugosidad_mm', 'La rugosidad relativa ε/D no puede superar 0,05.')
    return Instalacion(longitud, diametro / 1000, desnivel, rugosidad / 1000, k)


def validar_curva(puntos: Sequence[tuple[object, object]]) -> CurvaBomba:
    """Recibe filas (m³/h, m) en su orden original y devuelve una curva SI."""
    if not 3 <= len(puntos) <= 10:
        raise ErrorEntrada('puntos', 'Introduce entre 3 y 10 puntos de bomba.')
    convertidos = []
    for indice, fila in enumerate(puntos, 1):
        if not isinstance(fila, (list, tuple)) or len(fila) != 2:
            raise ErrorEntrada(f'puntos.{indice}', 'Cada fila debe contener caudal y altura.')
        campo_q = f'puntos.{indice}.caudal_m3h'
        campo_h = f'puntos.{indice}.altura_m'
        q = numero_decimal(fila[0], campo_q)
        h = numero_decimal(fila[1], campo_h)
        _rango(q, 0, 100, campo_q)
        _rango(h, 0, 200, campo_h)
        convertidos.append(PuntoBomba(q / 3600, h))
    return CurvaBomba(tuple(convertidos))


def validar_objetivo(caudal_m3h: object = None) -> float | None:
    """Meta opcional común en m³/s; el vacío no equivale a un caudal cero."""
    if caudal_m3h is None or (isinstance(caudal_m3h, str) and not caudal_m3h.strip()):
        return None
    q = numero_decimal(caudal_m3h, 'objetivo_m3h')
    _rango(q, 0, 100, 'objetivo_m3h', positivo=True)
    return q / 3600
