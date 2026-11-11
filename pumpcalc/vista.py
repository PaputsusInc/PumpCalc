"""Formulario y resultados NiceGUI de un escenario de bombeo."""

from nicegui import context, ui

from pumpcalc.detalle import mostrar_detalle
from pumpcalc.comparacion import ComparacionEscenarios, MENSAJES_META
from pumpcalc.ejemplos import EJEMPLOS
from pumpcalc.escena import VistaAnimacion
from pumpcalc.friccion import ErrorConvergencia
from pumpcalc.presentacion import opciones_curvas
from pumpcalc.panel_comparacion import mostrar_comparacion
from pumpcalc.tema import aplicar_tema


ESTADOS = {
    'pendiente': 'Cálculo pendiente',
    'datos_invalidos': 'Datos inválidos',
    'solucion': 'Solución encontrada',
    'sin_interseccion': 'Ausencia de intersección',
    'falta_convergencia': 'Falta de convergencia',
}
REGIMENES = {
    'sin_flujo': 'Sin flujo', 'laminar': 'Laminar',
    'transicion': 'Transición', 'turbulento': 'Turbulento',
}


def numero(valor: float, decimales: int = 6) -> str:
    return f'{valor:.{decimales}f}'.replace('.', ',')


def construir_vista() -> None:
    cliente = context.client
    proyecto = ComparacionEscenarios()
    sesion = proyecto.sesiones['A']
    campos: dict[str, ui.input] = {}
    temporizadores = {}
    restaurando = False
    escenas: dict[str, VistaAnimacion] = {}

    def error_campo(clave: str) -> str | None:
        return str(sesion.error) if sesion.error is not None and sesion.error.campo == clave else None

    def actualizar() -> None:
        for entrada in campos.values():
            entrada.validate()
        if proyecto.comparando:
            vistas_escenas.classes(add='pc-comparing')
        else:
            vistas_escenas.classes(remove='pc-comparing')
        for nombre, escena in escenas.items():
            escena.sesion = proyecto.sesiones[nombre]
            escena.contenedor.set_visibility(proyecto.comparando or nombre == proyecto.activo)
            escena.actualizar()
        metas.refresh()
        comparacion.refresh()
        resultados.refresh()

    def cancelar_temporizador(nombre: str | None = None) -> None:
        temporizador = temporizadores.pop(nombre or proyecto.activo, None)
        if temporizador is not None:
            temporizador.cancel()
            temporizador.delete()

    def programar() -> None:
        cancelar_temporizador()
        actualizar()
        if sesion.estado == 'pendiente':
            nombre = proyecto.activo
            sesion_programada = sesion
            revision = sesion.revision

            def recalcular() -> None:
                temporizadores.pop(nombre, None)
                if (proyecto.sesiones[nombre] is sesion_programada
                        and sesion_programada.simular_revision(revision)):
                    actualizar()

            # La fila que originó el evento puede desaparecer al refrescar la
            # tabla. El temporizador pertenece a la página, no a esa fila.
            with cliente:
                temporizadores[nombre] = ui.timer(0.2, recalcular, once=True)

    def editar_instalacion(clave: str, valor: str) -> None:
        if not restaurando:
            sesion.editar_instalacion(clave, valor)
            programar()

    def editar_punto(indice: int, columna: int, valor: str) -> None:
        sesion.editar_punto(indice, columna, valor)
        programar()

    def simular() -> None:
        cancelar_temporizador()
        sesion.simular()
        actualizar()

    async def reflejar_sesion() -> None:
        nonlocal restaurando
        restaurando = True
        try:
            selector.set_value(proyecto.activo)
            for clave, valor in sesion.entradas.items():
                campos[clave].set_value(valor)
            await tabla.refresh()
        finally:
            restaurando = False

    async def cambiar_activo(nombre: str) -> None:
        nonlocal sesion
        proyecto.seleccionar(nombre)
        sesion = proyecto.sesiones[nombre]
        await reflejar_sesion()
        actualizar()

    async def cargar_ejemplo(nombre: str = 'base') -> None:
        cancelar_temporizador()
        proyecto.cargar_ejemplo(nombre)
        await reflejar_sesion()
        actualizar()

    async def copiar() -> None:
        cancelar_temporizador('B')
        proyecto.copiar_a_b()
        escenas['B'].movimiento.fase_px = escenas['A'].movimiento.fase_px
        escenas['B'].movimiento.pausada = escenas['A'].movimiento.pausada
        await cambiar_activo('B')
        if sesion.estado == 'pendiente':
            programar()

    def cambiar_comparacion(valor: bool) -> None:
        proyecto.comparando = bool(valor)
        actualizar()

    def cambiar_objetivo(valor: str) -> None:
        proyecto.establecer_objetivo(valor)
        objetivo.validate()
        metas.refresh()

    @ui.refreshable
    def metas() -> None:
        with ui.element('div').classes('pc-meta-grid'):
            for nombre in proyecto.sesiones:
                evaluacion = proyecto.evaluar_meta(nombre)
                with ui.element('div').classes(f'pc-meta pc-meta-{nombre.lower()}'):
                    ui.label(f'{nombre}: {MENSAJES_META[evaluacion.estado]}')
                    if evaluacion.margen_m3s is not None:
                        with ui.element('small'):
                            ui.label(f'Margen {nombre}: {numero(evaluacion.margen_m3s * 3600)} m³/h')

    @ui.refreshable
    def comparacion() -> None:
        mostrar_comparacion(proyecto)

    async def agregar() -> None:
        if sesion.agregar_punto():
            await tabla.refresh()
            programar()

    async def quitar(indice: int) -> None:
        if sesion.quitar_punto(indice):
            await tabla.refresh()
            programar()

    def entrada(clave: str, etiqueta: str, valor: str, callback) -> ui.input:
        control = ui.input(
            etiqueta, value=valor, on_change=callback,
            validation=lambda _, clave=clave: error_campo(clave),
        ).props('outlined dense inputmode=decimal').classes('w-full')
        control.without_auto_validation()
        campos[clave] = control
        return control

    @ui.refreshable
    def tabla() -> None:
        for clave in list(campos):
            if clave.startswith('puntos.'):
                campos.pop(clave)
        with ui.element('table').classes('pc-pump-table text-left'):
            with ui.element('thead'):
                with ui.element('tr'):
                    for titulo in ('Punto', 'Caudal (m³/h)', 'Altura (m)', ''):
                        with ui.element('th'):
                            ui.label(titulo)
            with ui.element('tbody'):
                for indice, (q, h) in enumerate(sesion.puntos):
                    with ui.element('tr'):
                        with ui.element('td').classes('p-2 align-top'):
                            ui.label(str(indice + 1)).classes('pt-2')
                        with ui.element('td').classes('p-2 align-top'):
                            entrada(
                                f'puntos.{indice + 1}.caudal_m3h', f'Caudal del punto {indice + 1}', q,
                                lambda e, i=indice: editar_punto(i, 0, e.value),
                            )
                        with ui.element('td').classes('p-2 align-top'):
                            entrada(
                                f'puntos.{indice + 1}.altura_m', f'Altura del punto {indice + 1}', h,
                                lambda e, i=indice: editar_punto(i, 1, e.value),
                            )
                        with ui.element('td').classes('p-2 align-top'):
                            boton = ui.button(
                                icon='delete_outline', on_click=lambda i=indice: quitar(i),
                            ).props(f'flat round aria-label="Quitar punto {indice + 1}"').mark(
                                f'quitar-punto-{indice + 1}'
                            )
                            boton.set_enabled(len(sesion.puntos) > 3)
        boton = ui.button('Agregar punto', icon='add', on_click=agregar).props('outline')
        boton.set_enabled(len(sesion.puntos) < 10)

    @ui.refreshable
    def resultados() -> None:
        with ui.card().classes('pc-panel w-full'):
            seccion(f'Resultados · Escenario {proyecto.activo}', 'El equilibrio de tu instalación.', 'insights')
            ui.label(ESTADOS[sesion.estado]).classes(f'pc-status pc-status-{sesion.estado}').props(
                'role=status aria-live=polite'
            )
            if sesion.error is not None:
                ui.label(str(sesion.error)).classes('text-red-700')
                ui.label('Corrige el dato señalado para volver a simular.').classes('text-slate-600')
            elif sesion.estado == 'pendiente':
                ui.label('Esperando a que termines de editar para recalcular.').classes('text-slate-600')
            elif sesion.resultado is not None:
                ui.label(sesion.resultado.mensaje).classes('text-slate-600')
                punto = sesion.resultado.punto
                if punto is not None:
                    sistema = punto.sistema
                    f = sistema.friccion.factor_darcy
                    indicadores = [
                        ('Caudal de operación', numero(punto.caudal_m3s * 3600), 'm³/h'),
                        ('Altura de operación', numero(punto.altura_m), 'm'),
                        ('Velocidad del agua', numero(sistema.velocidad_ms), 'm/s'),
                        ('Pérdida en tubería', numero(sistema.perdida_tuberia_m), 'm'),
                        ('Pérdida en accesorios', numero(sistema.perdida_accesorios_m), 'm'),
                        ('Número de Reynolds', numero(sistema.reynolds, 2), ''),
                        ('Factor de Darcy', 'No aplicable' if f is None else numero(f, 8), ''),
                        ('Régimen de flujo', REGIMENES[sistema.friccion.regimen], ''),
                    ]
                    with ui.element('div').classes('pc-kpis'):
                        for indice, (etiqueta, valor, unidad) in enumerate(indicadores[:3]):
                            with ui.element('div').classes(f'pc-kpi pc-kpi-{indice}'):
                                ui.label(etiqueta).classes('pc-kpi-label')
                                ui.label(f'{valor} {unidad}'.strip()).classes('pc-kpi-value')
                    with ui.element('div').classes('pc-metrics'):
                        for etiqueta, valor, unidad in indicadores[3:]:
                            with ui.column().classes('pc-metric'):
                                ui.label(etiqueta).classes('pc-metric-label')
                                ui.label(f'{valor} {unidad}'.strip()).classes('pc-metric-value')
                    if sistema.friccion.advertencia:
                        ui.label(sistema.friccion.advertencia).classes('text-amber-800')
                    ui.label('H representa altura de energía, no una presión medida.').classes(
                        'text-sm text-slate-600'
                    )
                if sesion.escenario is not None and not proyecto.comparando:
                    ui.separator()
                    seccion('Curvas de bomba y sistema', 'Donde se cruzan, el sistema encuentra su caudal.', 'show_chart')
                    try:
                        opciones = opciones_curvas(sesion.escenario, sesion.resultado)
                        ui.echart(opciones, renderer='svg').classes('w-full').style('height:420px')
                        ui.label(
                            'Sistema: 150 muestras. Bomba: segmentos de los puntos ingresados. '
                            'El marcador procede de la bisección, no de las muestras de la gráfica.'
                        ).classes('text-sm text-slate-600')
                    except ErrorConvergencia as error:
                        ui.label(f'No se pudo completar la curva del sistema: {error}').classes('text-red-700')
                mostrar_detalle(sesion.resultado)

    def seccion(titulo: str, subtitulo: str, icono: str) -> None:
        with ui.element('div').classes('pc-section-head'):
            ui.icon(icono, size='20px').classes('pc-section-icon').props('aria-hidden=true')
            with ui.column().classes('gap-0'):
                ui.label(titulo).classes('pc-section-title')
                ui.label(subtitulo).classes('pc-section-subtitle')

    aplicar_tema()
    with ui.header().classes('pc-header items-center gap-3'):
        ui.icon('water_drop', size='23px').classes('pc-logo').props('aria-hidden=true')
        ui.label('PumpCalc').classes('pc-brand')
        ui.label('Explora. Compara. Entiende.').classes('pc-header-note')
        with ui.row().classes('pc-local'):
            ui.icon('circle').props('aria-hidden=true')
            ui.label('Tu laboratorio local')
    with ui.column().classes('pc-main'):
        with ui.element('section').classes('pc-hero'):
            with ui.element('div'):
                ui.label('EL AGUA SE MUEVE. TÚ EXPERIMENTAS.').classes('pc-eyebrow')
                ui.html('<h1>Pon tus ideas<br>a <span>fluir.</span></h1>')
                ui.label('Cambia una variable. Descubre el equilibrio. '
                         'Mira cómo una misma bomba cuenta dos historias distintas.').classes('pc-hero-copy')
                with ui.element('div').classes('pc-methods'):
                    for metodo in ('01 · Interpolación', '02 · Colebrook', '03 · Bisección'):
                        ui.label(metodo)
            with ui.element('div').classes('pc-hero-art').props('aria-hidden=true'):
                ui.element('div').classes('pc-orbit')
                ui.icon('water_drop', size='116px').classes('pc-hero-water')
                ui.html('<div class="pc-hero-equation"><strong>v = Q / A</strong>'
                        '<small>MÁS CAUDAL ≠ MÁS VELOCIDAD</small></div>')
        with ui.card().classes('pc-panel pc-toolbar w-full'):
            with ui.element('div').classes('pc-toolbar-main'):
                ui.label('EXPERIMENTA').classes('pc-eyebrow')
                selector = ui.toggle(['A', 'B'], value='A', on_change=
                                     lambda e: cambiar_activo(e.value) if not restaurando else None).mark(
                    'selector-escenario'
                ).props('unelevated aria-label="Escenario activo"')
                ui.button('Simular', icon='play_arrow', on_click=simular).classes('pc-action').props('unelevated')
                ui.button('Copiar A en B', icon='content_copy', on_click=copiar).props('outline')
                ui.button('Cargar caso base', icon='restart_alt', on_click=lambda: cargar_ejemplo()).props('flat')
                ui.switch('Comparar A y B', on_change=lambda e: cambiar_comparacion(e.value))
            with ui.element('div').classes('pc-example-row'):
                ejemplo = ui.select(EJEMPLOS, label='Ejemplo', value='base').props('outlined dense')
                ui.button('Cargar ejemplo', icon='science', on_click=lambda: cargar_ejemplo(ejemplo.value)).props('flat')
                ui.label('Tres puntos de partida. Todas tus preguntas. Datos ficticios.').classes('pc-example-note')
        with ui.element('div').classes('pc-lab'):
            with ui.element('aside').classes('pc-config'):
                with ui.card().classes('pc-panel w-full'):
                    seccion('Instalación', 'Dale forma a tu experimento.', 'tune')
                    ui.label('Acepta coma o punto decimal, sin separadores de miles.').classes('text-xs text-slate-600')
                    with ui.element('div').classes('pc-input-grid'):
                        for clave, etiqueta in (
                            ('longitud_m', 'Longitud total L (m)'),
                            ('diametro_mm', 'Diámetro interno D (mm)'),
                            ('desnivel_m', 'Desnivel Δz (m)'),
                            ('rugosidad_mm', 'Rugosidad ε (mm)'),
                            ('k_total', 'K total (sin unidad)'),
                        ):
                            entrada(clave, etiqueta, sesion.entradas[clave],
                                    lambda e, clave=clave: editar_instalacion(clave, e.value))
                with ui.card().classes('pc-panel w-full'):
                    seccion('Curva de la bomba', 'Los datos que ponen todo en marcha.', 'ssid_chart')
                    ui.label('De 3 a 10 puntos: caudal creciente y altura no creciente.').classes(
                        'text-sm text-slate-600'
                    )
                    tabla()
                with ui.card().classes('pc-panel pc-target w-full'):
                    seccion('Una meta, dos escenarios', '¿Hasta dónde llega cada configuración?', 'flag')
                    objetivo = ui.input('Caudal objetivo común (m³/h, opcional)', value=proyecto.objetivo_texto,
                                        on_change=lambda e: cambiar_objetivo(e.value),
                                        validation=lambda _: str(proyecto.error_objetivo)
                                        if proyecto.error_objetivo else None).props('outlined inputmode=decimal').classes('w-full')
                    metas()
            with ui.element('section').classes('pc-stage'):
                with ui.element('div').classes('pc-scenes') as vistas_escenas:
                    for nombre, estado_sesion in proyecto.sesiones.items():
                        escenas[nombre] = VistaAnimacion(estado_sesion, nombre)
                        escenas[nombre].contenedor.set_visibility(nombre == 'A')
                comparacion()
                resultados()
        with ui.element('footer').classes('pc-footer'):
            ui.html('<strong>PumpCalc</strong> · Entender el flujo cambia la perspectiva.')
            ui.label('Modelo educativo · Niveles fijos · Los resultados no certifican una instalación real.')
