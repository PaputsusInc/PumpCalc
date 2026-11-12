"""Formulario y resultados NiceGUI de un escenario de bombeo."""

from nicegui import context, ui

from pumpcalc.comparacion import ComparacionEscenarios, MENSAJES_META
from pumpcalc.ejemplos import EJEMPLOS
from pumpcalc.escena import VistaAnimacion
from pumpcalc.panel_comparacion import mostrar_comparacion
from pumpcalc.presentacion import formatear_numero
from pumpcalc.resultados import mostrar_resultados
from pumpcalc.tema import aplicar_tema, encabezado_seccion


def construir_vista() -> None:
    """Crea los controles y las dos sesiones que pertenecen a esta página."""
    cliente = context.client
    proyecto = ComparacionEscenarios()
    sesion = proyecto.sesiones['A']
    campos: dict[str, ui.input] = {}
    temporizadores = {}
    restaurando = False
    escenas: dict[str, VistaAnimacion] = {}

    def error_campo(clave: str) -> str | None:
        if clave in sesion.errores_datos_bomba:
            return sesion.errores_datos_bomba[clave]
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
                # Comprueba identidad y revisión por si cambiaron B o sus entradas.
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

    def editar_dato_bomba(clave: str, valor: str) -> None:
        if not restaurando:
            sesion.editar_dato_bomba(clave, valor)
            for campo in sesion.datos_bomba:
                campos[campo].validate()
            if proyecto.comparando:
                comparacion.refresh()

    def simular() -> None:
        cancelar_temporizador()
        sesion.simular()
        actualizar()

    async def reflejar_sesion() -> None:
        nonlocal restaurando
        # Al mostrar valores ya guardados, los eventos del formulario no son ediciones.
        restaurando = True
        try:
            selector.set_value(proyecto.activo)
            for clave, valor in sesion.entradas.items():
                campos[clave].set_value(valor)
            for clave, valor in sesion.datos_bomba.items():
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

    def cambiar_vista(modo: str) -> None:
        for escena in escenas.values():
            escena.seleccionar_vista(modo)

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
                            ui.label(f'Margen {nombre}: {formatear_numero(evaluacion.margen_m3s * 3600)} m³/h')

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
                    for titulo in ('#', 'Caudal (m³/h)', 'Altura (m)', ''):
                        with ui.element('th'):
                            ui.label(titulo)
            with ui.element('tbody'):
                for indice, (q, h) in enumerate(sesion.puntos):
                    with ui.element('tr'):
                        with ui.element('td').classes('p-2 align-top'):
                            ui.label(str(indice + 1)).classes('pt-2')
                        # Cada callback captura la fila y la columna de su celda.
                        for columna, (clave, etiqueta, valor) in enumerate((
                            ('caudal_m3h', 'Caudal', q),
                            ('altura_m', 'Altura', h),
                        )):
                            with ui.element('td').classes('p-2 align-top'):
                                entrada(
                                    f'puntos.{indice + 1}.{clave}',
                                    f'{etiqueta} del punto {indice + 1}',
                                    valor,
                                    lambda e, i=indice, c=columna: editar_punto(i, c, e.value),
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
        mostrar_resultados(sesion, proyecto.activo, comparando=proyecto.comparando)

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
                    encabezado_seccion('Instalación', 'Dale forma a tu experimento.', 'tune')
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
                    encabezado_seccion('Curva de la bomba', 'Los datos que ponen todo en marcha.', 'ssid_chart')
                    ui.label('Datos generales del escenario (opcionales)').classes('text-sm font-semibold')
                    with ui.element('div').classes('pc-bomba-grid'):
                        for clave, etiqueta in (
                            ('potencia_hp', 'Potencia (HP)'),
                            ('altura_maxima_m', 'Hmax (m)'),
                            ('caudal_maximo_m3h', 'Qmax (m³/h)'),
                        ):
                            entrada(clave, etiqueta, sesion.datos_bomba[clave],
                                    lambda e, clave=clave: editar_dato_bomba(clave, e.value))
                    ui.label('Potencia nominal del motor, altura máxima y caudal máximo. '
                             'Son referencias: Hmax y Qmax no forman un mismo punto. '
                             'El cálculo usa los puntos Q–H de abajo.').classes('text-xs text-slate-600')
                    ui.label('De 3 a 10 puntos: caudal creciente y altura no creciente.').classes(
                        'text-sm text-slate-600'
                    )
                    tabla()
                with ui.card().classes('pc-panel pc-target w-full'):
                    encabezado_seccion('Una meta, dos escenarios', '¿Hasta dónde llega cada configuración?', 'flag')
                    objetivo = ui.input('Caudal objetivo común (m³/h, opcional)', value=proyecto.objetivo_texto,
                                        on_change=lambda e: cambiar_objetivo(e.value),
                                        validation=lambda _: str(proyecto.error_objetivo)
                                        if proyecto.error_objetivo else None).props('outlined inputmode=decimal').classes('w-full')
                    metas()
            with ui.element('section').classes('pc-stage'):
                with ui.element('div').classes('pc-view-switch'):
                    ui.label('Visualización del agua').classes('pc-view-switch-label')
                    ui.toggle(['3D', '2D'], value='3D', on_change=lambda e: cambiar_vista(e.value)).props(
                        'unelevated aria-label="Cambiar visualización entre 3D y 2D"'
                    ).mark('selector-vista')
                with ui.element('div').classes('pc-scenes') as vistas_escenas:
                    for nombre, estado_sesion in proyecto.sesiones.items():
                        escenas[nombre] = VistaAnimacion(estado_sesion, nombre, '3D')
                        escenas[nombre].contenedor.set_visibility(nombre == 'A')
                comparacion()
                resultados()
        with ui.element('footer').classes('pc-footer'):
            ui.html('<strong>PumpCalc</strong> · Entender el flujo cambia la perspectiva.')
            ui.label('Modelo educativo · Cálculo estacionario · Visualización ilustrativa · '
                     'Los resultados no certifican una instalación real.')
