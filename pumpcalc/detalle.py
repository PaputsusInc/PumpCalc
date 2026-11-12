"""Panel NiceGUI con los métodos y la evidencia del resultado vigente."""

from nicegui import ui

from pumpcalc.friccion import MAX_ITERACIONES_COLEBROOK, TOLERANCIA_COLEBROOK
from pumpcalc.operacion import ResultadoOperacion
from pumpcalc.presentacion import filas_biseccion, filas_colebrook


def cientifico(valor: float) -> str:
    return f'{valor:.5e}'.replace('.', ',')


def tabla_numerica(filas: list[dict], columnas: list[tuple[str, str]]) -> None:
    """Formatea las trazas del motor para leer iteraciones y residuos."""
    presentadas = [
        {clave: valor if clave == 'iteracion' else '—' if valor is None else cientifico(valor)
         for clave, valor in fila.items()}
        for fila in filas
    ]
    with ui.element('div').classes('w-full overflow-x-auto'):
        ui.table(
            columns=[{'name': clave, 'field': clave, 'label': etiqueta, 'align': 'right'}
                     for clave, etiqueta in columnas],
            rows=presentadas, row_key='iteracion', pagination=10,
        ).props('dense flat').classes('w-full')


def mostrar_detalle(resultado: ResultadoOperacion) -> None:
    with ui.expansion('Detalle numérico', icon='functions').classes('pc-detail w-full'):
        ui.label('Bisección del balance de alturas').classes('text-lg font-semibold')
        ui.label('F(Q) = Hb(Q) − Hs(Q). El intervalo se registra antes de dividirlo.')
        solver = resultado.biseccion
        if solver is not None:
            controles = solver.parametros
            ui.label(
                f'Tolerancia de caudal τQ: {cientifico(controles.tolerancia_x * 3600)} m³/h '
                f'({cientifico(controles.tolerancia_x)} m³/s). '
                f'Tolerancia de altura τH: {cientifico(controles.tolerancia_f)} m. '
                f'Máximo: {controles.max_iteraciones} iteraciones.'
            )
            ui.label(f'Iteraciones de bisección: {solver.iteraciones}.')
            if solver.residuo is not None:
                ui.label(f'Residuo final F(Q): {cientifico(solver.residuo)} m.')
            if solver.cota_error is not None:
                ui.label(f'Cota numérica de caudal: {cientifico(solver.cota_error * 3600)} m³/h.')
            filas = filas_biseccion(resultado)
            if filas:
                tabla_numerica(filas, [
                    ('iteracion', 'Iteración'), ('a', 'a (m³/h)'), ('b', 'b (m³/h)'),
                    ('c', 'c (m³/h)'), ('ea', 'Ea(Q) (m³/h)'),
                    ('residuo', 'F(c) (m)'), ('cota', 'Semiancho (m³/h)'),
                ])
                ui.label('Ea(Q) = |cᵢ − cᵢ₋₁|. En la primera iteración no hay un c anterior; '
                         'el semiancho es la cota del intervalo.').classes('text-sm text-slate-600')
            elif resultado.punto is not None:
                ui.label('Raíz exacta en un extremo: no se requirió dividir el intervalo.')
            else:
                ui.label('No hay cambio de signo en el dominio de la curva; no se ejecutó bisección.')
        else:
            ui.label('El fallo de fricción impidió completar la bisección.')
        ui.label(
            'La cota localiza la raíz del modelo bajo una evaluación suficientemente precisa '
            'de F; no mide la incertidumbre física de la bomba o la instalación.'
        ).classes('text-sm text-slate-600')

        punto = resultado.punto
        if punto is None:
            ui.label('No hay un punto válido para mostrar un tramo o factor de fricción final.')
            return
        ui.separator()
        ui.label('Interpolación de la bomba').classes('text-lg font-semibold')
        izquierdo, derecho = punto.tramo
        ui.label(
            f'Tramo: ({izquierdo.caudal_m3s * 3600:.6f} m³/h, {izquierdo.altura_m:.6f} m) '
            f'a ({derecho.caudal_m3s * 3600:.6f} m³/h, {derecho.altura_m:.6f} m).'
        )
        ui.label('Hb(Q) = Hi + (Hi+1 − Hi) · (Q − Qi) / (Qi+1 − Qi). Sin extrapolación.')
        ui.separator()
        ui.label('Factor de fricción de Darcy').classes('text-lg font-semibold')
        friccion = punto.sistema.friccion
        if friccion.regimen == 'sin_flujo':
            ui.label('Q = 0: factor no aplicable; no se evalúa 64/Re ni Colebrook.')
        elif friccion.regimen == 'laminar':
            ui.label('Flujo laminar: f = 64/Re. No requiere iteración.')
        else:
            if friccion.regimen == 'transicion':
                ui.label('Transición: interpolación didáctica entre f₂₀₀₀ y f₄₀₀₀.')
                ui.label('Las iteraciones siguientes corresponden al cálculo auxiliar de f₄₀₀₀.')
            else:
                ui.label('Flujo turbulento: Colebrook por iteración de punto fijo.')
            colebrook = friccion.colebrook
            ui.label(
                f'Colebrook en Re = {colebrook.reynolds:.6f}: '
                f'f = {colebrook.factor_darcy:.10f}; {colebrook.iteraciones} iteraciones.'
            )
            ui.label(
                f'x = 1/√f; x₀ = 1/√0,02. Ea(x) y |G(x)| '
                f'≤ {cientifico(TOLERANCIA_COLEBROOK)}; máximo {MAX_ITERACIONES_COLEBROOK} iteraciones.'
            )
            tabla_numerica(filas_colebrook(resultado), [
                ('iteracion', 'Iteración'), ('x_anterior', 'x anterior'), ('x', 'x'),
                ('cambio', 'Ea(x) = |xᵢ − xᵢ₋₁|'), ('residuo', 'G(x)'),
            ])
