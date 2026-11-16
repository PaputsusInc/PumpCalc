"""Panel que convierte una sesión de cálculo en indicadores, curvas y detalle."""

from nicegui import ui

from pumpcalc.detalle import mostrar_detalle
from pumpcalc.entradas import Escenario
from pumpcalc.friccion import ErrorConvergencia
from pumpcalc.operacion import PuntoOperacion, ResultadoOperacion
from pumpcalc.presentacion import formatear_numero, opciones_curvas
from pumpcalc.simulacion import SesionSimulacion
from pumpcalc.tema import encabezado_seccion


ESTADOS = {
    'pendiente': 'Cálculo pendiente',
    'datos_invalidos': 'Datos inválidos',
    'solucion': 'Solución encontrada',
    'sin_interseccion': 'Ausencia de intersección',
    'falta_convergencia': 'Falta de convergencia',
}
REGIMENES = {
    'sin_flujo': 'Sin flujo',
    'laminar': 'Laminar',
    'transicion': 'Transición',
    'turbulento': 'Turbulento',
}


def mostrar_resultados(
    sesion: SesionSimulacion, nombre: str, *, comparando: bool
) -> None:
    """Muestra la información que está disponible para la sesión activa."""
    with ui.card().classes('pc-panel w-full'):
        encabezado_seccion(
            f'Resultados · Escenario {nombre}', 'El equilibrio de tu instalación.', 'insights',
        )
        ui.label(ESTADOS[sesion.estado]).classes(f'pc-status pc-status-{sesion.estado}').props(
            'role=status aria-live=polite'
        )
        if sesion.error is not None:
            ui.label(str(sesion.error)).classes('text-red-700')
            ui.label('Corrige el dato señalado para volver a simular.').classes('text-slate-600')
            return
        if sesion.estado == 'pendiente':
            ui.label('Esperando a que termines de editar para recalcular.').classes('text-slate-600')
            return

        resultado = sesion.resultado
        if resultado is None:
            return
        ui.label(resultado.mensaje).classes('text-slate-600')
        punto = sesion.punto_vigente
        if punto is not None:
            _mostrar_indicadores(punto)
        if sesion.escenario is not None and not comparando:
            _mostrar_curvas(sesion.escenario, resultado)
        mostrar_detalle(resultado)


def _mostrar_indicadores(punto: PuntoOperacion) -> None:
    sistema = punto.sistema
    friccion = sistema.friccion
    factor = friccion.factor_darcy
    principales = (
        ('Caudal de operación', f'{formatear_numero(punto.caudal_m3s * 3600)} m³/h'),
        ('Altura de operación', f'{formatear_numero(punto.altura_m)} m'),
        ('Velocidad del agua', f'{formatear_numero(sistema.velocidad_ms)} m/s'),
    )
    complementarios = (
        ('Pérdida en tubería', f'{formatear_numero(sistema.perdida_tuberia_m)} m'),
        ('Pérdida en accesorios', f'{formatear_numero(sistema.perdida_accesorios_m)} m'),
        ('Número de Reynolds', formatear_numero(sistema.reynolds, 2)),
        ('Factor de Darcy', 'No aplicable' if factor is None else formatear_numero(factor, 8)),
        ('Régimen de flujo', REGIMENES[friccion.regimen]),
    )
    with ui.element('div').classes('pc-kpis'):
        for indice, (etiqueta, valor) in enumerate(principales):
            with ui.element('div').classes(f'pc-kpi pc-kpi-{indice}'):
                ui.label(etiqueta).classes('pc-kpi-label')
                ui.label(valor).classes('pc-kpi-value')
    with ui.element('div').classes('pc-metrics'):
        for etiqueta, valor in complementarios:
            with ui.column().classes('pc-metric'):
                ui.label(etiqueta).classes('pc-metric-label')
                ui.label(valor).classes('pc-metric-value')
    if friccion.advertencia:
        ui.label(friccion.advertencia).classes('text-amber-800')
    ui.label('H representa altura de energía, no una presión medida.').classes(
        'text-sm text-slate-600'
    )


def _mostrar_curvas(escenario: Escenario, resultado: ResultadoOperacion) -> None:
    ui.separator()
    encabezado_seccion(
        'Curvas de bomba y sistema', 'Donde se cruzan, el sistema encuentra su caudal.', 'show_chart',
    )
    try:
        opciones = opciones_curvas(escenario, resultado)
    except ErrorConvergencia as error:
        ui.label(f'No se pudo completar la curva del sistema: {error}').classes('text-red-700')
        return
    ui.echart(opciones, renderer='svg').classes('w-full').style('height:420px')
    ui.label(
        'Sistema: 150 muestras. Bomba: segmentos de los puntos ingresados. '
        'El marcador procede de la bisección, no de las muestras de la gráfica.'
    ).classes('text-sm text-slate-600')
