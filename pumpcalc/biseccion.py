"""Bisección propia con cota del intervalo y control simultáneo del residuo."""

from collections.abc import Callable
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class ParametrosBiseccion:
    # Valores predeterminados para Q en m³/s y F en metros de altura.
    tolerancia_x: float = 1e-7
    tolerancia_f: float = 1e-4
    max_iteraciones: int = 80

    def __post_init__(self) -> None:
        for tolerancia in (self.tolerancia_x, self.tolerancia_f):
            if not math.isfinite(tolerancia) or tolerancia <= 0:
                raise ValueError('Las tolerancias deben ser finitas y positivas.')
        if (isinstance(self.max_iteraciones, bool)
                or not isinstance(self.max_iteraciones, int) or self.max_iteraciones < 1):
            raise ValueError('El límite de iteraciones debe ser un entero positivo.')


@dataclass(frozen=True)
class IteracionBiseccion:
    iteracion: int
    a: float
    b: float
    c: float
    f_c: float
    semiancho: float


@dataclass(frozen=True)
class ResultadoBiseccion:
    estado: str
    raiz: float | None
    residuo: float | None
    cota_error: float | None
    traza: tuple[IteracionBiseccion, ...]
    parametros: ParametrosBiseccion
    signo_extremos: int | None = None

    @property
    def iteraciones(self) -> int:
        return len(self.traza)


def biseccion(funcion: Callable[[float], float], a: float, b: float, *,
              parametros: ParametrosBiseccion = ParametrosBiseccion()) -> ResultadoBiseccion:
    """Resuelve una función continua; no extrapola fuera de [a, b].

    El registro conserva el intervalo antes de partirlo. La cota describe la
    localización numérica de la raíz, no la incertidumbre física del modelo.
    """
    if not all(math.isfinite(x) for x in (a, b, b - a)) or a >= b:
        raise ValueError('El intervalo debe tener extremos finitos y amplitud positiva finita.')

    def evaluar(x: float) -> float:
        valor = funcion(x)
        if not math.isfinite(valor):
            raise ValueError('La función produjo un valor no finito durante la bisección.')
        return valor

    f_a = evaluar(a)
    if f_a == 0:
        return ResultadoBiseccion('solucion', a, 0, 0, (), parametros)
    f_b = evaluar(b)
    if f_b == 0:
        return ResultadoBiseccion('solucion', b, 0, 0, (), parametros)
    # Comparar signos directamente evita subdesbordamiento al multiplicarlos.
    if (f_a > 0) == (f_b > 0):
        return ResultadoBiseccion(
            'sin_interseccion', None, None, None, (), parametros,
            signo_extremos=1 if f_a > 0 else -1,
        )

    traza = []
    for numero in range(1, parametros.max_iteraciones + 1):
        semiancho = (b - a) / 2
        c = a + semiancho
        f_c = evaluar(c)
        traza.append(IteracionBiseccion(numero, a, b, c, f_c, semiancho))
        if f_c == 0:
            return ResultadoBiseccion('solucion', c, 0, 0, tuple(traza), parametros)
        if semiancho <= parametros.tolerancia_x and abs(f_c) <= parametros.tolerancia_f:
            return ResultadoBiseccion('solucion', c, f_c, semiancho, tuple(traza), parametros)
        if (f_a > 0) == (f_c > 0):
            a, f_a = c, f_c
        else:
            b = c
    return ResultadoBiseccion(
        'falta_convergencia', None, traza[-1].f_c, traza[-1].semiancho,
        tuple(traza), parametros,
    )
