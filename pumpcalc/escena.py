"""Escena NiceGUI: fondo de instalación y trazas actualizadas por Python."""

from time import perf_counter

from nicegui import ui

from pumpcalc.animacion import (
    ALTO_ESCENA, ANCHO_ESCENA, MovimientoFlujo, capa_trazas,
    fondo_instalacion, fuente_svg, grosor_tuberia,
)
from pumpcalc.simulacion import SesionSimulacion


class VistaAnimacion:
    def __init__(self, sesion: SesionSimulacion) -> None:
        self.sesion = sesion
        self.movimiento = MovimientoFlujo()
        self.ultimo_fotograma = perf_counter()
        self.grosor = 24.0
        self.fondo = ''
        with ui.card().classes('w-full p-5 gap-3'):
            with ui.row().classes('items-center justify-between w-full'):
                ui.label('Agua en la instalación').classes('text-xl font-semibold')
                self.boton = ui.button('Pausar animación', icon='pause', on_click=self.alternar).props('outline')
            self.estado = ui.label().classes('text-sm text-slate-600').props('role=status aria-live=polite')
            self.imagen = ui.interactive_image(size=(ANCHO_ESCENA, ALTO_ESCENA)).classes(
                'w-full max-w-4xl mx-auto'
            ).props('aria-label="Flujo de agua entre dos depósitos a través de una bomba y tubería"')
            ui.label('Movimiento ilustrativo · Niveles fijos; no simula el llenado de tanques.').classes(
                'text-sm text-slate-600'
            )
            self.temporizador = ui.timer(1 / 30, self.fotograma, immediate=False)
        self.actualizar()

    def actualizar(self) -> None:
        instalacion = self.sesion.escenario.instalacion if self.sesion.escenario is not None else None
        self.movimiento.sincronizar(self.sesion.estado, self.sesion.resultado)
        self.grosor = grosor_tuberia(instalacion.diametro_m) if instalacion is not None else 24
        svg = fondo_instalacion(instalacion, self.sesion.resultado)
        if svg != self.fondo:
            self.fondo = svg
            self.imagen.set_source(fuente_svg(svg))
        self.imagen.set_content(capa_trazas(self.movimiento.fase_px, self.grosor))
        self.ultimo_fotograma = perf_counter()
        self.actualizar_estado()

    def actualizar_estado(self) -> None:
        estados = {
            'pendiente': 'Movimiento suspendido: cálculo pendiente.',
            'datos_invalidos': 'Movimiento suspendido: datos inválidos.',
            'sin_interseccion': 'Movimiento suspendido: ausencia de intersección.',
            'falta_convergencia': 'Movimiento suspendido: falta de convergencia.',
        }
        if self.sesion.estado != 'solucion':
            texto = estados[self.sesion.estado]
        elif self.movimiento.velocidad_ms == 0:
            texto = 'Sin movimiento: solución válida con Q = 0.'
        elif self.movimiento.pausada:
            texto = 'Animación pausada. El resultado hidráulico se mantiene.'
        else:
            texto = 'Animación en movimiento según la velocidad calculada.'
        self.estado.set_text(texto)
        self.boton.set_text('Reanudar animación' if self.movimiento.pausada else 'Pausar animación')
        self.boton.set_enabled(self.sesion.estado == 'solucion')

    def alternar(self) -> None:
        self.movimiento.pausada = not self.movimiento.pausada
        self.ultimo_fotograma = perf_counter()
        self.actualizar_estado()

    def fotograma(self) -> None:
        ahora = perf_counter()
        segundos = ahora - self.ultimo_fotograma
        self.ultimo_fotograma = ahora
        # Consulta siempre el estado vigente, incluso durante refrescos asíncronos.
        self.movimiento.sincronizar(self.sesion.estado, self.sesion.resultado)
        if self.movimiento.avanzar(segundos):
            self.imagen.set_content(capa_trazas(self.movimiento.fase_px, self.grosor))
