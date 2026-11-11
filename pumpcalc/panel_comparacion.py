"""Resumen y curvas de dos configuraciones independientes."""

from nicegui import ui

from pumpcalc.comparacion import ComparacionEscenarios
from pumpcalc.friccion import ErrorConvergencia
from pumpcalc.presentacion import opciones_comparacion


def mostrar_comparacion(proyecto: ComparacionEscenarios) -> None:
    if not proyecto.comparando:
        return
    with ui.card().classes('w-full p-6 gap-4').mark('comparacion'):
        ui.label('Comparación de escenarios A y B').classes('text-xl font-semibold')
        diferencia = proyecto.diferencia_caudal()
        if diferencia is None:
            ui.label('Comparación de caudal no disponible: faltan resultados vigentes en A o B.')
        else:
            ui.label(f'Cambio B − A: {diferencia.cambio_m3s * 3600:+.6f} m³/h.')
            ui.label(f'Diferencia absoluta: {diferencia.diferencia_absoluta_m3s * 3600:.6f} m³/h.')
            ui.label('Porcentaje respecto de A: no aplicable (Q de A es cero).'
                     if diferencia.porcentaje is None else
                     f'Variación respecto de A: {diferencia.porcentaje:+.3f} %.')
        filas = []
        for clave, etiqueta in (
            ('longitud_m', 'Longitud L (m)'), ('diametro_mm', 'Diámetro D (mm)'),
            ('desnivel_m', 'Desnivel Δz (m)'), ('rugosidad_mm', 'Rugosidad ε (mm)'),
            ('k_total', 'K total'),
        ):
            filas.append({'dato': etiqueta, **{n: s.entradas[clave] for n, s in proyecto.sesiones.items()}})
        filas.append({'dato': 'Puntos de bomba (m³/h; m)', **{
            n: ' · '.join(f'({q}; {h})' for q, h in s.puntos) for n, s in proyecto.sesiones.items()
        }})
        filas.append({'dato': 'Estado', **{n: s.estado.replace('_', ' ') for n, s in proyecto.sesiones.items()}})
        for etiqueta, obtener in (
            ('Q (m³/h)', lambda p: p.caudal_m3s * 3600),
            ('H (m)', lambda p: p.altura_m), ('v (m/s)', lambda p: p.sistema.velocidad_ms),
        ):
            fila = {'dato': etiqueta}
            for nombre, sesion in proyecto.sesiones.items():
                punto = sesion.resultado.punto if sesion.estado == 'solucion' and sesion.resultado else None
                fila[nombre] = 'No disponible' if punto is None else f'{obtener(punto):.6f}'
            filas.append(fila)
        ui.table(columns=[{'name': c, 'field': c, 'label': c if c != 'dato' else 'Dato', 'align': 'left'}
                          for c in ('dato', 'A', 'B')], rows=filas, row_key='dato').props(
            'flat wrap-cells'
        ).classes('w-full')
        casos = {n: (s.escenario, s.resultado) for n, s in proyecto.sesiones.items()
                 if s.escenario is not None and s.resultado is not None}
        if casos:
            try:
                ui.echart(opciones_comparacion(casos), renderer='svg').classes('w-full').style('height:460px')
                ui.label('Cada curva conserva su dominio. Las curvas pendientes o inválidas se retiran.').classes(
                    'text-sm text-slate-600'
                )
            except ErrorConvergencia as error:
                ui.label(f'No se pudo completar la curva del sistema: {error}').classes('text-red-700')
