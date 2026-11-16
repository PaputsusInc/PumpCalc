"""Datos de gráficas y tablas derivados del modelo, sin controles NiceGUI."""

from pumpcalc.entradas import Escenario
from pumpcalc.operacion import ResultadoOperacion
from pumpcalc.perdidas import evaluar_sistema


MUESTRAS_GRAFICA = 150


def formatear_numero(valor: float, decimales: int = 6) -> str:
    """Redondea para pantalla y muestra el separador decimal en español."""
    return f'{valor:.{decimales}f}'.replace('.', ',')


def opciones_curvas(escenario: Escenario, resultado: ResultadoOperacion, *,
                     muestras: int = MUESTRAS_GRAFICA) -> dict:
    """Muestrea Hs; la bomba se dibuja por sus segmentos exactos.

    El marcador siempre procede del solver. El muestreo gráfico no resuelve
    el cruce ni prolonga las curvas fuera de su dominio.
    """
    return _opciones_grafica(
        escenario.curva.dominio_m3s, _series_curvas(escenario, resultado, muestras)
    )


def _series_curvas(
    escenario: Escenario, resultado: ResultadoOperacion, muestras: int
) -> list[dict]:
    if isinstance(muestras, bool) or not isinstance(muestras, int) or muestras < 2:
        raise ValueError('Se requieren al menos dos muestras para dibujar el sistema.')
    a, b = escenario.curva.dominio_m3s
    caudales = [a + (b - a) * i / (muestras - 1) for i in range(muestras)]
    # Fija los extremos para que el redondeo no saque una muestra del dominio.
    caudales[0], caudales[-1] = a, b
    sistema = [[q * 3600, evaluar_sistema(escenario.instalacion, q).altura_sistema_m]
               for q in caudales]
    bomba = [[p.caudal_m3s * 3600, p.altura_m] for p in escenario.curva.puntos]
    series = [
        {'name': 'Bomba interpolada', 'type': 'line', 'data': bomba,
         'showSymbol': False, 'smooth': False, 'lineStyle': {'color': '#087f8c', 'width': 3.5}},
        {'name': 'Sistema', 'type': 'line', 'data': sistema,
         'showSymbol': False, 'smooth': False,
         'lineStyle': {'color': '#d97716', 'width': 3, 'type': 'dashed'}},
        {'name': 'Puntos de bomba', 'type': 'scatter', 'data': bomba, 'symbolSize': 8,
         'itemStyle': {'color': '#087f8c', 'borderColor': '#ffffff', 'borderWidth': 2}},
    ]
    if resultado.punto is not None and resultado.estado == 'solucion':
        punto = resultado.punto
        series.append({
            'name': 'Punto de operación', 'type': 'scatter', 'symbol': 'diamond',
            'symbolSize': 17, 'data': [[punto.caudal_m3s * 3600, punto.altura_m]],
            'itemStyle': {'color': '#633bd6', 'borderColor': '#ffffff', 'borderWidth': 2}, 'z': 10,
        })
    return series


def _opciones_grafica(dominio: tuple[float, float], series: list[dict]) -> dict:
    a, b = dominio
    return {
        'animation': False,
        'textStyle': {'fontFamily': 'Segoe UI, sans-serif', 'color': '#526b7c'},
        'tooltip': {'trigger': 'axis', 'backgroundColor': '#082b3a', 'borderColor': '#315462',
                    'textStyle': {'color': '#e2f5f5'}, 'padding': 12},
        'legend': {'top': 0, 'type': 'scroll', 'itemWidth': 18, 'itemHeight': 9,
                   'textStyle': {'color': '#456375', 'fontSize': 11}},
        'grid': {'top': 60, 'left': 14, 'right': 28, 'bottom': 45, 'containLabel': True},
        'xAxis': {'type': 'value', 'name': 'Caudal Q (m³/h)', 'nameLocation': 'middle',
                  'nameGap': 32, 'min': a * 3600, 'max': b * 3600,
                  'axisLine': {'lineStyle': {'color': '#c6d8e2'}},
                  'axisLabel': {'color': '#526b7c'},
                  'splitLine': {'lineStyle': {'color': '#e7eff3', 'type': 'dashed'}}},
        'yAxis': {'type': 'value', 'name': 'Altura H (m)', 'min': 0,
                  'axisLabel': {'color': '#526b7c'},
                  'splitLine': {'lineStyle': {'color': '#e7eff3', 'type': 'dashed'}}},
        'series': series,
    }


def filas_biseccion(resultado: ResultadoOperacion) -> list[dict]:
    """Convierte a m³/h y calcula Ea entre puntos medios consecutivos."""
    if resultado.biseccion is None:
        return []
    filas = []
    c_anterior = None
    for paso in resultado.biseccion.traza:
        filas.append({
            'iteracion': paso.iteracion, 'a': paso.a * 3600, 'b': paso.b * 3600,
            'c': paso.c * 3600,
            'ea': None if c_anterior is None else abs(paso.c - c_anterior) * 3600,
            'residuo': paso.f_c, 'cota': paso.semiancho * 3600,
        })
        c_anterior = paso.c
    return filas


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
    for nombre, (escenario, resultado) in casos.items():
        dominios.append(escenario.curva.dominio_m3s)
        color = '#087f8c' if nombre == 'A' else '#633bd6'
        for serie in _series_curvas(escenario, resultado, MUESTRAS_GRAFICA):
            serie['name'] += f' ({nombre})'
            if serie['type'] == 'line':
                serie['lineStyle']['color'] = color
            else:
                serie['itemStyle']['color'] = color
            series.append(serie)
    # El eje abarca ambos dominios. Cada serie conserva sus propias muestras.
    dominio = min(a for a, _ in dominios), max(b for _, b in dominios)
    return _opciones_grafica(dominio, series)
