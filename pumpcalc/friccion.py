"""Factor de Darcy: flujo laminar, transición didáctica y Colebrook propio."""

from dataclasses import dataclass
import math

from pumpcalc.entradas import ErrorEntrada


TOLERANCIA_COLEBROOK = 1e-10
MAX_ITERACIONES_COLEBROOK = 100


@dataclass(frozen=True)
class IteracionColebrook:
    iteracion: int
    x_anterior: float
    x: float
    cambio: float
    residuo: float


class ErrorConvergencia(RuntimeError):
    """Fallo explícito de fricción que debe propagarse al resolver el sistema."""

    def __init__(self, mensaje: str, traza: tuple[IteracionColebrook, ...] = ()) -> None:
        super().__init__(mensaje)
        self.traza = traza


@dataclass(frozen=True)
class ResultadoColebrook:
    reynolds: float
    factor_darcy: float
    traza: tuple[IteracionColebrook, ...]

    @property
    def iteraciones(self) -> int:
        return len(self.traza)


@dataclass(frozen=True)
class ResultadoFriccion:
    factor_darcy: float | None
    regimen: str
    colebrook: ResultadoColebrook | None = None
    advertencia: str | None = None


def _validar_dominio(reynolds: float, rugosidad_relativa: float) -> None:
    if not math.isfinite(reynolds) or reynolds < 0:
        raise ErrorEntrada('reynolds', 'Reynolds debe ser finito y no negativo.')
    if not math.isfinite(rugosidad_relativa) or not 0 <= rugosidad_relativa <= 0.05:
        raise ErrorEntrada('rugosidad_relativa', 'ε/D debe estar entre 0 y 0,05.')


def _punto_fijo(x: float, reynolds: float, rugosidad_relativa: float) -> float:
    argumento = rugosidad_relativa / 3.7 + 2.51 * x / reynolds
    if not math.isfinite(argumento) or argumento <= 0:
        raise ErrorConvergencia('Colebrook: argumento del logaritmo inválido.')
    siguiente = -2 * math.log10(argumento)
    if not math.isfinite(siguiente) or siguiente <= 0:
        raise ErrorConvergencia('Colebrook: la iteración produjo un x inválido.')
    return siguiente


def colebrook(reynolds: float, rugosidad_relativa: float, *,
              tolerancia: float = TOLERANCIA_COLEBROOK,
              max_iteraciones: int = MAX_ITERACIONES_COLEBROOK) -> ResultadoColebrook:
    """Resuelve x = 1/√f por punto fijo; exige cambio y residuo pequeños."""
    _validar_dominio(reynolds, rugosidad_relativa)
    if reynolds < 4000:
        raise ErrorEntrada('reynolds', 'Colebrook requiere Re mayor o igual a 4000.')
    if not math.isfinite(tolerancia) or tolerancia <= 0:
        raise ValueError('La tolerancia de Colebrook debe ser finita y positiva.')
    if isinstance(max_iteraciones, bool) or not isinstance(max_iteraciones, int) or max_iteraciones < 1:
        raise ValueError('El límite de iteraciones debe ser un entero positivo.')

    x = 1 / math.sqrt(0.02)
    traza = []
    for numero in range(1, max_iteraciones + 1):
        nuevo = _punto_fijo(x, reynolds, rugosidad_relativa)
        cambio = abs(nuevo - x)
        # G(x) = x - phi(x); se evalúa en el nuevo x, no en el anterior.
        residuo = nuevo - _punto_fijo(nuevo, reynolds, rugosidad_relativa)
        traza.append(IteracionColebrook(numero, x, nuevo, cambio, residuo))
        if cambio <= tolerancia and abs(residuo) <= tolerancia:
            return ResultadoColebrook(reynolds, 1 / nuevo ** 2, tuple(traza))
        x = nuevo
    raise ErrorConvergencia(
        f'Colebrook no convergió en {max_iteraciones} iteraciones.', tuple(traza)
    )


def factor_friccion(reynolds: float, rugosidad_relativa: float, *,
                    max_iteraciones: int = MAX_ITERACIONES_COLEBROOK) -> ResultadoFriccion:
    """En transición, la traza pertenece al cálculo auxiliar de f en Re = 4000."""
    _validar_dominio(reynolds, rugosidad_relativa)
    if reynolds == 0:
        return ResultadoFriccion(None, 'sin_flujo')
    if reynolds <= 2000:
        return ResultadoFriccion(64 / reynolds, 'laminar')
    if reynolds < 4000:
        auxiliar = colebrook(4000, rugosidad_relativa, max_iteraciones=max_iteraciones)
        t = (reynolds - 2000) / 2000
        f = (1 - t) * (64 / 2000) + t * auxiliar.factor_darcy
        return ResultadoFriccion(
            f, 'transicion', auxiliar,
            'Zona de transición: aproximación didáctica; las iteraciones corresponden a f₄₀₀₀.',
        )
    resultado = colebrook(reynolds, rugosidad_relativa, max_iteraciones=max_iteraciones)
    return ResultadoFriccion(resultado.factor_darcy, 'turbulento', resultado)
