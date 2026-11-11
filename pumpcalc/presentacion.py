"""Datos de gráficas y tablas derivados del modelo, sin controles NiceGUI."""

from pumpcalc.entradas import Escenario
from pumpcalc.operacion import ResultadoOperacion
from pumpcalc.perdidas import evaluar_sistema


MUESTRAS_GRAFICA = 150


def opciones_curvas(escenario: Escenario, resultado: ResultadoOperacion, *,
                     muestras: int = MUESTRAS_GRAFICA) -> dict:
    """Muestrea Hs; la bomba se dibuja por sus segmentos exactos.

    El marcador siempre procede del solver. El muestreo gráfico no resuelve
    el cruce ni prolonga las curvas fuera de su dominio.
    """
    if isinstance(muestras, bool) or not isinstance(muestras, int) or muestras < 2:
        raise ValueError('Se requieren al menos dos muestras para dibujar el sistema.')
    a, b = escenario.curva.dominio_m3s
    caudales = [a + (b - a) * i / (muestras - 1) for i in range(muestras)]
    caudales[0], caudales[-1] = a, b
    sistema = [[q * 3600, evaluar_sistema(escenario.instalacion, q).altura_sistema_m]
               for q in caudales]
    bomba = [[p.caudal_m3s * 3600, p.altura_m] for p in escenario.curva.puntos]
    series = [
        {'name': 'Bomba interpolada', 'type': 'line', 'data': bomba,
         'showSymbol': False, 'smooth': False, 'lineStyle': {'color': '#036b80', 'width': 3}},
        {'name': 'Sistema', 'type': 'line', 'data': sistema,
         'showSymbol': False, 'smooth': False,
         'lineStyle': {'color': '#b45309', 'width': 3, 'type': 'dashed'}},
        {'name': 'Puntos de bomba', 'type': 'scatter', 'data': bomba, 'symbolSize': 8,
         'itemStyle': {'color': '#036b80'}},
    ]
    if resultado.punto is not None and resultado.estado == 'solucion':
        punto = resultado.punto
        series.append({
            'name': 'Punto de operación', 'type': 'scatter', 'symbol': 'diamond',
            'symbolSize': 15, 'data': [[punto.caudal_m3s * 3600, punto.altura_m]],
            'itemStyle': {'color': '#7e22ce'}, 'z': 10,
        })
    return {
        'animation': False,
        'tooltip': {'trigger': 'axis'},
        'legend': {'top': 0, 'type': 'scroll'},
        'grid': {'top': 55, 'left': 55, 'right': 20, 'bottom': 60, 'containLabel': True},
        'xAxis': {'type': 'value', 'name': 'Caudal Q (m³/h)', 'nameLocation': 'middle',
                  'nameGap': 35, 'min': a * 3600, 'max': b * 3600},
        'yAxis': {'type': 'value', 'name': 'Altura H (m)', 'min': 0},
        'series': series,
    }


def filas_biseccion(resultado: ResultadoOperacion) -> list[dict]:
    """Convierte a m³/h solo para presentación; los residuos siguen en m."""
    if resultado.biseccion is None:
        return []
    return [
        {'iteracion': paso.iteracion, 'a': paso.a * 3600, 'b': paso.b * 3600,
         'c': paso.c * 3600, 'residuo': paso.f_c, 'cota': paso.semiancho * 3600}
        for paso in resultado.biseccion.traza
    ]


def filas_colebrook(resultado: ResultadoOperacion) -> list[dict]:
    """Solo la fricción del punto final, auxiliar f₄₀₀₀ si está en transición."""
    if resultado.punto is None or resultado.punto.sistema.friccion.colebrook is None:
        return []
    return [
        {'iteracion': paso.iteracion, 'x_anterior': paso.x_anterior, 'x': paso.x,
         'cambio': paso.cambio, 'residuo': paso.residuo}
        for paso in resultado.punto.sistema.friccion.colebrook.traza
    ]


def opciones_comparacion(casos: dict[str, tuple[Escenario, ResultadoOperacion]]) -> dict:
    """Superpone casos vigentes, conservando el dominio propio de cada serie."""
    if not casos:
        raise ValueError('No hay curvas vigentes para comparar.')
    series = []
    dominios = []
    opciones = None
    for nombre, (escenario, resultado) in casos.items():
        actuales = opciones_curvas(escenario, resultado)
        if opciones is None:
            opciones = actuales
        dominios.append(escenario.curva.dominio_m3s)
        color = '#036b80' if nombre == 'A' else '#7e22ce'
        for serie in actuales['series']:
            serie['name'] += f' ({nombre})'
            if serie['type'] == 'line':
                serie['lineStyle']['color'] = color
            else:
                serie['itemStyle']['color'] = color
            series.append(serie)
    opciones['series'] = series
    opciones['xAxis']['min'] = min(a for a, _ in dominios) * 3600
    opciones['xAxis']['max'] = max(b for _, b in dominios) * 3600
    return opciones
