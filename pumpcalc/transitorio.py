"""Llenado de dos depósitos por Runge–Kutta 4, independiente de la vista 3D.

El estado integrado es el volumen transferido. Así se conserva exactamente el
volumen total: lo que sale del origen entra en el destino. En cada evaluación
de la derivada se resuelve de nuevo el punto de operación para el desnivel
instantáneo. No se extrapola la curva de la bomba.
"""

from dataclasses import dataclass, replace
from collections.abc import Callable
import math

from pumpcalc.entradas import ErrorEntrada, Escenario, numero_decimal
from pumpcalc.operacion import resolver_operacion


@dataclass(frozen=True)
class Tanque:
    area_m2: float
    capacidad_m3: float
    inicial_m3: float

    def __post_init__(self) -> None:
        if not 0.1 <= self.area_m2 <= 20 or not math.isfinite(self.area_m2):
            raise ErrorEntrada('area_m2', 'El área debe estar entre 0,1 y 20 m².')
        if not 0.05 <= self.capacidad_m3 <= 20 or not math.isfinite(self.capacidad_m3):
            raise ErrorEntrada('capacidad_m3', 'La capacidad debe estar entre 0,05 y 20 m³.')
        if not math.isfinite(self.inicial_m3) or not 0 <= self.inicial_m3 <= self.capacidad_m3:
            raise ErrorEntrada('inicial_m3', 'El volumen inicial debe estar entre 0 y la capacidad.')


@dataclass(frozen=True)
class ConfiguracionTanques:
    origen: Tanque
    destino: Tanque


def validar_tanques(datos: dict[str, str]) -> ConfiguracionTanques:
    """Valida las seis entradas visibles y conserva la clave del campo erróneo."""
    tanques = {}
    for nombre in ('origen', 'destino'):
        valores = {}
        for magnitud in ('area_m2', 'capacidad_m3', 'inicial_m3'):
            clave = f'{nombre}_{magnitud}'
            valores[magnitud] = numero_decimal(datos[clave], clave)
        try:
            tanques[nombre] = Tanque(**valores)
        except ErrorEntrada as error:
            raise ErrorEntrada(f'{nombre}_{error.campo}', str(error)) from None
    return ConfiguracionTanques(**tanques)


@dataclass(frozen=True)
class EstadoLlenado:
    tiempo_s: float
    origen_m3: float
    destino_m3: float
    caudal_m3s: float
    velocidad_ms: float


@dataclass(frozen=True)
class TrayectoriaLlenado:
    estados: tuple[EstadoLlenado, ...]
    motivo_parada: str


def paso_runge_kutta4(derivada: Callable[[float], float], valor: float, paso: float) -> float:
    """Un paso RK4 clásico para y' = derivada(y), sin biblioteca de integración."""
    k1 = derivada(valor)
    k2 = derivada(valor + paso * k1 / 2)
    k3 = derivada(valor + paso * k2 / 2)
    k4 = derivada(valor + paso * k3)
    return paso * (k1 + 2 * k2 + 2 * k3 + k4) / 6


def simular_llenado(escenario: Escenario, tanques: ConfiguracionTanques, *,
                    paso_s: float = 10, horizonte_s: float = 7200) -> TrayectoriaLlenado:
    """Integra dV/dt = Q(V) con RK4 clásico y topes físicos de ambos tanques.

    El desnivel del formulario corresponde a los niveles *iniciales*. El
    cambio posterior es V/A en cada tanque. El horizonte limita la vista,
    no representa una condición de parada hidráulica.
    """
    if not math.isfinite(paso_s) or paso_s <= 0 or not math.isfinite(horizonte_s) or horizonte_s <= 0:
        raise ValueError('El paso y el horizonte deben ser finitos y positivos.')
    origen, destino = tanques.origen, tanques.destino
    maximo = min(origen.inicial_m3, destino.capacidad_m3 - destino.inicial_m3)
    cache: dict[float, tuple[float, float, str | None]] = {}

    def flujo(transferido: float) -> tuple[float, float, str | None]:
        transferido = min(max(transferido, 0), maximo)
        if transferido >= maximo - 1e-12:
            return 0, 0, 'Origen vacío o destino lleno'
        if transferido not in cache:
            desnivel = (escenario.instalacion.desnivel_m
                        + transferido / destino.area_m2 + transferido / origen.area_m2)
            if desnivel > 100:
                cache[transferido] = (0, 0, 'Desnivel fuera del dominio del modelo')
            else:
                instalacion = replace(escenario.instalacion, desnivel_m=desnivel)
                resultado = resolver_operacion(replace(escenario, instalacion=instalacion))
                if resultado.punto is None:
                    motivo = ('La bomba no tiene cruce en la curva disponible' if resultado.estado == 'sin_interseccion'
                              else resultado.mensaje)
                    cache[transferido] = (0, 0, motivo)
                else:
                    cache[transferido] = (resultado.punto.caudal_m3s,
                                           resultado.punto.sistema.velocidad_ms, None)
        return cache[transferido]

    def estado(tiempo: float, transferido: float) -> EstadoLlenado:
        q, velocidad, _ = flujo(transferido)
        return EstadoLlenado(tiempo, origen.inicial_m3 - transferido,
                             destino.inicial_m3 + transferido, q, velocidad)

    estados = [estado(0, 0)]
    transferido = 0.0
    tiempo = 0.0
    motivo = 'Horizonte de simulación alcanzado'
    while tiempo < horizonte_s - 1e-9:
        q1, _, fallo = flujo(transferido)
        if fallo or q1 <= 0:
            motivo = fallo or 'Caudal nulo'
            break
        dt = min(paso_s, horizonte_s - tiempo)
        # Cerca del tope, RK4 evalúa el caudal justo antes de la pared. La
        # detención se aplica al final del paso, sin sesgar las etapas k2–k4.
        limite_etapa = max(0, maximo - 1e-10)
        incremento = paso_runge_kutta4(
            lambda volumen: flujo(min(volumen, limite_etapa))[0], transferido, dt)
        nuevo = min(maximo, transferido + max(0, incremento))
        if nuevo <= transferido:
            motivo = 'Caudal nulo'
            break
        # En el último paso se interpola el instante de llegada al límite.
        if nuevo == maximo and incremento > 0:
            dt *= (maximo - transferido) / incremento
        tiempo += dt
        transferido = nuevo
        estados.append(estado(tiempo, transferido))
    if transferido >= maximo - 1e-12:
        motivo = 'Origen vacío o destino lleno'
    return TrayectoriaLlenado(tuple(estados), motivo)
