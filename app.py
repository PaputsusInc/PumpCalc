"""Entrada de la aplicación web local de PumpCalc."""

from nicegui import ui


@ui.page('/')
def inicio() -> None:
    """Vista inicial; el cálculo se incorporará en los siguientes pasos."""
    ui.colors(primary='#036b80')
    with ui.header().classes('items-center gap-3'):
        ui.icon('water_drop', size='2rem')
        ui.label('PumpCalc').classes('text-2xl font-semibold')
        ui.label('Simulador de bombeo').classes('text-base')

    with ui.column().classes('w-full max-w-5xl mx-auto p-6 gap-6'):
        ui.label('Explora cómo cambia el caudal de una bomba').classes(
            'text-3xl font-semibold'
        )
        ui.label(
            'Una bomba, una tubería y dos depósitos abiertos. '
            'Un espacio para experimentar y comprender el punto de operación.'
        ).classes('text-lg text-slate-600')

        with ui.card().classes('w-full p-6 gap-3'):
            ui.label('Bienvenido a PumpCalc').classes('text-xl font-semibold')
            ui.label(
                'La aplicación está en preparación. Próximamente podrás '
                'configurar la instalación, simular el flujo y comparar '
                'dos escenarios.'
            )
            ui.label('Los cálculos y la animación aún no están disponibles.').classes(
                'text-slate-600'
            )

        ui.label(
            'Modelo educativo de flujo estacionario. Los resultados de la '
            'versión completa serán estimaciones, no una certificación de '
            'una instalación real.'
        ).classes('text-sm text-slate-600')


if __name__ == '__main__':
    ui.run(
        host='127.0.0.1',
        port=8080,
        title='PumpCalc · Simulador de bombeo',
        language='es',
        reload=False,
        show=False,
    )
