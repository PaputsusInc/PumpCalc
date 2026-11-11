"""Punto de operación que integra bomba, pérdidas y bisección en SI."""

from dataclasses import dataclass

from pumpcalc.biseccion import ParametrosBiseccion, ResultadoBiseccion, biseccion
from pumpcalc.entradas import Escenario, PuntoBomba
from pumpcalc.friccion import ErrorConvergencia, MAX_ITERACIONES_COLEBROOK
from pumpcalc.interpolacion import altura_bomba
from pumpcalc.perdidas import ResultadoSistema, evaluar_sistema


@dataclass(frozen=True)
class PuntoOperacion:
    caudal_m3s: float
    altura_m: float
    sistema: ResultadoSistema
    tramo: tuple[PuntoBomba, PuntoBomba]


@dataclass(frozen=True)
class ResultadoOperacion:
    estado: str
    mensaje: str
    punto: PuntoOperacion | None
    biseccion: ResultadoBiseccion | None
    metodo_fallido: str | None = None


def resolver_operacion(escenario: Escenario, *,
                       parametros: ParametrosBiseccion = ParametrosBiseccion(),
                       max_iteraciones_colebrook: int = MAX_ITERACIONES_COLEBROOK) -> ResultadoOperacion:
    """Busca el cruce exactamente en el dominio ingresado de la bomba.

    La traza de fricción retenida es únicamente la del resultado final.
    Una falta de solución nunca se representa mediante un caudal cero.
    """
    def sistema(q: float) -> ResultadoSistema:
        return evaluar_sistema(
            escenario.instalacion, q, max_iteraciones_colebrook=max_iteraciones_colebrook,
        )

    def diferencia(q: float) -> float:
        return altura_bomba(escenario.curva, q) - sistema(q).altura_sistema_m

    try:
        # El intervalo pertenece a los datos de bomba, no a las muestras de la gráfica.
        a, b = escenario.curva.dominio_m3s
        resultado = biseccion(diferencia, a, b, parametros=parametros)
        if resultado.estado == 'sin_interseccion':
            posicion = 'por encima' if resultado.signo_extremos == 1 else 'por debajo'
            return ResultadoOperacion(
                'sin_interseccion',
                f'La curva de la bomba queda {posicion} de la del sistema '
                'en el intervalo disponible. No hay intersección dentro de esos datos.',
                None, resultado,
            )
        if resultado.estado == 'falta_convergencia':
            return ResultadoOperacion(
                'falta_convergencia',
                f'Bisección no convergió en {parametros.max_iteraciones} iteraciones.',
                None, resultado, 'biseccion',
            )

        q = resultado.raiz
        final = sistema(q)
        for izquierdo, derecho in zip(escenario.curva.puntos, escenario.curva.puntos[1:]):
            if izquierdo.caudal_m3s <= q <= derecho.caudal_m3s:
                tramo = (izquierdo, derecho)
                break
        punto = PuntoOperacion(q, altura_bomba(escenario.curva, q), final, tramo)
        return ResultadoOperacion('solucion', 'Punto de operación encontrado en el modelo.', punto, resultado)
    except ErrorConvergencia as error:
        return ResultadoOperacion(
            'falta_convergencia', str(error), None, None, 'colebrook',
        )
