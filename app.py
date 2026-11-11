"""Entrada de la aplicación web local de PumpCalc."""

from nicegui import ui

from pumpcalc.vista import construir_vista


@ui.page('/')
def inicio() -> None:
    """Cada página conserva su propia sesión y comienza con el caso base."""
    construir_vista()


if __name__ == '__main__':
    ui.run(
        host='127.0.0.1',
        port=8080,
        title='PumpCalc · Simulador de bombeo',
        language='es',
        reload=False,
        show=False,
    )
