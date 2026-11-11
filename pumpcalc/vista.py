"""Formulario y resultados NiceGUI de un escenario de bombeo."""

from nicegui import ui

from pumpcalc.simulacion import SesionSimulacion


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
    sesion = SesionSimulacion()
    sesion.simular()
    campos: dict[str, ui.input] = {}
    temporizador = None
    restaurando = False

    def error_campo(clave: str) -> str | None:
        return str(sesion.error) if sesion.error is not None and sesion.error.campo == clave else None

    def actualizar() -> None:
        for entrada in campos.values():
            entrada.validate()
        resultados.refresh()

    def cancelar_temporizador() -> None:
        nonlocal temporizador
        if temporizador is not None:
            temporizador.cancel()
            temporizador.delete()
            temporizador = None

    def programar() -> None:
        nonlocal temporizador
        cancelar_temporizador()
        actualizar()
        if sesion.estado == 'pendiente':
            revision = sesion.revision

            def recalcular() -> None:
                nonlocal temporizador
                temporizador = None
                if sesion.simular_revision(revision):
                    actualizar()

            temporizador = ui.timer(0.2, recalcular, once=True)

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

    def cargar_base() -> None:
        nonlocal restaurando
        cancelar_temporizador()
        sesion.cargar_base()
        restaurando = True
        try:
            for clave, valor in sesion.entradas.items():
                campos[clave].set_value(valor)
            tabla.refresh()
        finally:
            restaurando = False
        simular()

    def agregar() -> None:
        if sesion.agregar_punto():
            tabla.refresh()
            programar()

    def quitar(indice: int) -> None:
        if sesion.quitar_punto(indice):
            tabla.refresh()
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
        with ui.element('table').classes('w-full border-collapse text-left'):
            with ui.element('thead'):
                with ui.element('tr'):
                    for titulo in ('Punto', 'Caudal (m³/h)', 'Altura (m)', ''):
                        with ui.element('th').classes('p-2 text-sm font-medium text-slate-600'):
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
                            ).props(f'flat round aria-label="Quitar punto {indice + 1}"')
                            boton.set_enabled(len(sesion.puntos) > 3)
        boton = ui.button('Agregar punto', icon='add', on_click=agregar).props('outline')
        boton.set_enabled(len(sesion.puntos) < 10)

    @ui.refreshable
    def resultados() -> None:
        with ui.card().classes('w-full p-6 gap-4'):
            ui.label('Resultados · Escenario A').classes('text-xl font-semibold')
            ui.label(ESTADOS[sesion.estado]).classes('text-lg font-medium').props(
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
                    with ui.element('div').classes('grid grid-cols-2 gap-x-6 gap-y-5 w-full'):
                        for etiqueta, valor, unidad in indicadores:
                            with ui.column().classes('gap-0'):
                                ui.label(etiqueta).classes('text-sm text-slate-600')
                                ui.label(f'{valor} {unidad}'.strip()).classes('text-xl font-semibold')
                    if sistema.friccion.advertencia:
                        ui.label(sistema.friccion.advertencia).classes('text-amber-800')
                    ui.label('H representa altura de energía, no una presión medida.').classes(
                        'text-sm text-slate-600'
                    )

    ui.colors(primary='#036b80')
    with ui.header().classes('items-center gap-3'):
        ui.icon('water_drop', size='2rem')
        ui.label('PumpCalc').classes('text-2xl font-semibold')
        ui.label('Simulador de bombeo').classes('text-base')
    with ui.column().classes('w-full max-w-7xl mx-auto p-6 gap-6'):
        ui.label('Simula tu instalación de bombeo').classes('text-3xl font-semibold')
        ui.label('Una bomba, una tubería y dos depósitos abiertos con niveles fijos.').classes(
            'text-lg text-slate-600'
        )
        with ui.row().classes('items-center gap-3'):
            ui.button('Simular', icon='play_arrow', on_click=simular)
            ui.button('Cargar caso base', icon='restart_alt', on_click=cargar_base).props('outline')
            ui.label('Ejemplo ficticio · Escenario A').classes('text-sm text-slate-600')
        with ui.element('div').classes('grid grid-cols-1 lg:grid-cols-2 gap-6 w-full items-start'):
            with ui.column().classes('w-full gap-6'):
                with ui.card().classes('w-full p-6 gap-4'):
                    ui.label('Instalación').classes('text-xl font-semibold')
                    ui.label('Acepta coma o punto decimal, sin separadores de miles.').classes(
                        'text-sm text-slate-600'
                    )
                    with ui.element('div').classes('grid grid-cols-1 sm:grid-cols-2 gap-4 w-full'):
                        for clave, etiqueta in (
                            ('longitud_m', 'Longitud total L (m)'),
                            ('diametro_mm', 'Diámetro interno D (mm)'),
                            ('desnivel_m', 'Desnivel Δz (m)'),
                            ('rugosidad_mm', 'Rugosidad ε (mm)'),
                            ('k_total', 'K total (sin unidad)'),
                        ):
                            entrada(clave, etiqueta, sesion.entradas[clave],
                                    lambda e, clave=clave: editar_instalacion(clave, e.value))
                with ui.card().classes('w-full p-6 gap-3'):
                    ui.label('Curva de la bomba').classes('text-xl font-semibold')
                    ui.label('De 3 a 10 puntos: caudal creciente y altura no creciente.').classes(
                        'text-sm text-slate-600'
                    )
                    tabla()
            with ui.column().classes('w-full lg:sticky lg:top-20'):
                resultados()
        ui.label(
            'Modelo educativo de flujo estacionario. Los datos iniciales son de demostración. '
            'Los resultados son estimaciones y no certifican una instalación real.'
        ).classes('text-sm text-slate-600')
