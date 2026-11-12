"""Escena NiceGUI: fondo de instalación y trazas actualizadas por Python."""

from time import perf_counter

from nicegui import ui

from pumpcalc.animacion import (
    ALTO_ESCENA, ANCHO_ESCENA, MovimientoFlujo, capa_trazas,
    fondo_instalacion, fuente_svg, grosor_tuberia, trayecto_instalacion,
)
from pumpcalc.escena3d import VistaEscena3D
from pumpcalc.simulacion import SesionSimulacion


class VistaAnimacion:
    """Muestra una sesión con un fondo SVG y una capa de trazas móviles."""

    def __init__(self, sesion: SesionSimulacion, nombre: str = 'A', modo: str = '3D') -> None:
        self.sesion = sesion
        self.modo = modo
        self.movimiento = MovimientoFlujo()
        self.ultimo_fotograma = perf_counter()
        self.grosor = 24.0
        self.fondo = ''
        self.contenedor = ui.card().classes(f'pc-panel pc-scene pc-scene-{nombre.lower()} w-full').mark(f'escena-{nombre}')
        with self.contenedor:
            with ui.row().classes('pc-scene-heading items-center justify-between w-full'):
                with ui.row().classes('items-center gap-2'):
                    ui.label(nombre).classes('pc-scene-letter')
                    ui.label(f'Escenario {nombre} · Agua en la instalación').classes('pc-section-title')
                with ui.row().classes('items-center gap-2'):
                    self.boton = ui.button('Pausar animación', icon='pause', on_click=self.alternar).props(
                        'outline color=white'
                    )
                    self.boton_reproducir = ui.button(
                        'Reproducir de nuevo', icon='replay', on_click=self.reproducir,
                    ).props('outline color=white').mark(f'reproducir-{nombre}')
            self.estado = ui.label().classes('pc-scene-status').props('role=status aria-live=polite')
            with ui.element('div').classes('pc-3d-shell w-full') as self.contenedor_3d:
                with ui.element('div').classes('pc-3d-viewport'):
                    self.vista_3d = VistaEscena3D(sesion)
                    self.aviso_3d = ui.label().classes('pc-3d-overlay-state')
                    ui.button(icon='center_focus_strong', on_click=self.vista_3d.reiniciar_camara).props(
                        'flat round color=white aria-label="Restablecer vista 3D"'
                    ).classes('pc-3d-reset').mark(f'restablecer-camara-{nombre}')
                with ui.element('div').classes('pc-3d-readout'):
                    self.lectura_q = ui.label()
                    self.lectura_v = ui.label()
                    self.lectura_nivel = ui.label()
                ui.label('Arrastra para girar · Desliza para acercar · Q regula la rapidez relativa. '
                         'El agua baja en origen y sube en destino; los niveles y la parada son ilustrativos.').classes(
                             'pc-scene-caption')
            with ui.element('div').classes('pc-2d-shell w-full') as self.contenedor_2d:
                self.imagen = ui.interactive_image(size=(ANCHO_ESCENA, ALTO_ESCENA)).classes(
                    'w-full max-w-4xl mx-auto'
                ).props('aria-label="Flujo de agua entre dos depósitos a través de una bomba y tubería"')
                ui.label('Movimiento ilustrativo · Niveles fijos; no simula el llenado de tanques.').classes(
                    'pc-scene-caption'
                )
            self.temporizador = ui.timer(1 / 30, self.fotograma, immediate=False)
        self.seleccionar_vista(modo)
        self.actualizar()

    def seleccionar_vista(self, modo: str) -> None:
        if modo not in ('2D', '3D'):
            raise ValueError('La vista debe ser 2D o 3D.')
        self.modo = modo
        self.contenedor_2d.set_visibility(modo == '2D')
        self.contenedor_3d.set_visibility(modo == '3D')

    def actualizar(self) -> None:
        instalacion = self.sesion.escenario.instalacion if self.sesion.escenario is not None else None
        self.movimiento.sincronizar(self.sesion.estado, self.sesion.resultado)
        if instalacion is not None:
            self.grosor = grosor_tuberia(instalacion.diametro_m)
            self.movimiento.trayecto = trayecto_instalacion(instalacion)
        svg = fondo_instalacion(instalacion, self.sesion.resultado, self.movimiento.trayecto)
        # El fondo cambia con el escenario. El temporizador solo mueve las trazas.
        if svg != self.fondo:
            self.fondo = svg
            self.imagen.set_source(fuente_svg(svg))
        self._dibujar_trazas()
        self.ultimo_fotograma = perf_counter()
        self.vista_3d.sesion = self.sesion
        self.vista_3d.actualizar(self.movimiento.pausada)
        punto = self.sesion.punto_vigente
        if punto is None:
            self.lectura_q.set_text('Q  — m³/h')
            self.lectura_v.set_text('v  — m/s')
        else:
            self.lectura_q.set_text(f'Q  {punto.caudal_m3s * 3600:.3f} m³/h')
            self.lectura_v.set_text(f'v  {punto.sistema.velocidad_ms:.3f} m/s')
        self.lectura_nivel.set_text('Desnivel Δz  — m' if instalacion is None else
                                    f'Desnivel Δz  {instalacion.desnivel_m:g} m')
        avisos = {
            'pendiente': 'Cálculo pendiente',
            'datos_invalidos': 'Datos inválidos · se muestra la última geometría válida',
            'sin_interseccion': 'Sin punto de operación en el intervalo ingresado',
            'falta_convergencia': 'No se obtuvo un punto de operación',
        }
        self.aviso_3d.set_text(avisos.get(self.sesion.estado, ''))
        self.aviso_3d.set_visibility(self.sesion.estado != 'solucion')
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
            texto = 'Visualización vinculada a la velocidad calculada.'
        self.estado.set_text(texto)
        self.boton.set_text('Reanudar animación' if self.movimiento.pausada else 'Pausar animación')
        self.boton.set_enabled(self.sesion.estado == 'solucion')
        self.boton_reproducir.set_enabled(
            self.sesion.estado == 'solucion' and self.movimiento.velocidad_ms is not None
            and self.movimiento.velocidad_ms > 0)

    def reproducir(self) -> None:
        """Reinicia el movimiento 2D y la transferencia visual 3D."""
        if self.sesion.estado != 'solucion' or not self.movimiento.velocidad_ms:
            return
        self.movimiento.pausada = False
        self.movimiento.fase_px = 0
        self.ultimo_fotograma = perf_counter()
        self._dibujar_trazas()
        self.vista_3d.actualizar(False)
        self.vista_3d.reproducir()
        self.actualizar_estado()

    def alternar(self) -> None:
        self.movimiento.pausada = not self.movimiento.pausada
        self.ultimo_fotograma = perf_counter()
        self.vista_3d.actualizar(self.movimiento.pausada)
        self.actualizar_estado()

    def _dibujar_trazas(self) -> None:
        movimiento = self.movimiento
        self.imagen.set_content(capa_trazas(movimiento.fase_px, self.grosor, movimiento.trayecto))

    def fotograma(self) -> None:
        ahora = perf_counter()
        segundos = ahora - self.ultimo_fotograma
        self.ultimo_fotograma = ahora
        if not self.contenedor.visible or self.modo != '2D':
            return
        # Consulta siempre el estado vigente, incluso durante refrescos asíncronos.
        self.movimiento.sincronizar(self.sesion.estado, self.sesion.resultado)
        if self.movimiento.avanzar(segundos):
            self._dibujar_trazas()
