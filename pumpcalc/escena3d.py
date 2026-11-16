"""Escena tridimensional ilustrativa conectada al punto de operación vigente."""

from dataclasses import dataclass
import math
from pathlib import Path
from uuid import uuid4

from nicegui import app, ui
from nicegui.elements.scene.scene_object3d import Object3D

from pumpcalc.entradas import Instalacion
from pumpcalc.simulacion import SesionSimulacion
from pumpcalc.transitorio import ConfiguracionTanques, TrayectoriaLlenado, simular_llenado


ASSETS = Path(__file__).parent / 'assets'
BOMBA_MODELO = Path(__file__).parents[1] / 'assets' / 'modelos' / 'bomba_usuario.glb'
BOMBA_URL = app.add_static_file(local_file=BOMBA_MODELO, url_path='/modelos/bomba_usuario.glb')
ANCHO_AGUA_ORIGEN = 2.05 - .15
ANCHO_AGUA_DESTINO = 2.2 - .15
FONDO_AGUA = 1.5 - .17
ALTURA_TOMA = .58
ALTURA_VISUAL_AGUA = .56
SEGUNDOS_SIMULADOS_POR_SEGUNDO = 60

class AguaEnTuberia(Object3D, component=ASSETS / 'agua_tuberia.js'):
    """Partículas animadas en el navegador para evitar fotogramas por WebSocket."""

    def __init__(self, puntos: list[list[float]], radio: float, escena_id: str) -> None:
        super().__init__(puntos, 65, radio, escena_id)
        self.rapidez = 0.0
        self.activa = False
        self.pausada = False

    def establecer_flujo(self, rapidez: float, activa: bool, pausada: bool) -> None:
        self.rapidez, self.activa, self.pausada = rapidez, activa, pausada
        self.run_method('set_flow', rapidez, activa, pausada)

    def _resend(self) -> None:
        super()._resend()
        self.run_method('set_flow', self.rapidez, self.activa, self.pausada)

    def reproducir(self) -> None:
        self.run_method('restart')


class SuperficieAgua(Object3D, component=ASSETS / 'superficie_agua.js'):
    """Agua del depósito de succión sincronizada con el llenado visual."""

    def __init__(self, ancho: float, fondo: float, base: float, nivel: float,
                 descenso: float, escena_id: str) -> None:
        super().__init__(ancho, fondo, base, nivel, descenso, escena_id)
        self.activa = False
        self.pausada = False

    def establecer_flujo(self, activa: bool, pausada: bool) -> None:
        self.activa, self.pausada = activa, pausada
        self.run_method('set_flow', activa, pausada)

    def _resend(self) -> None:
        super()._resend()
        self.run_method('set_flow', self.activa, self.pausada)

    def reproducir(self) -> None:
        self.run_method('restart')


class CanalAgua(Object3D, component=ASSETS / 'canal_agua.js'):
    """Cinta luminosa dentro de cada tramo visible de la tubería."""

    def __init__(self, puntos: list[list[float]], radio: float, escena_id: str) -> None:
        super().__init__(puntos, radio, escena_id)
        self.rapidez = 0.0
        self.activa = False
        self.pausada = False

    def establecer_flujo(self, rapidez: float, activa: bool, pausada: bool) -> None:
        self.rapidez, self.activa, self.pausada = rapidez, activa, pausada
        self.run_method('set_flow', rapidez, activa, pausada)

    def _resend(self) -> None:
        super()._resend()
        self.run_method('set_flow', self.rapidez, self.activa, self.pausada)

    def reproducir(self) -> None:
        self.run_method('restart')


class SueloLuminoso(Object3D, component=ASSETS / 'suelo_luminoso.js'):
    """Piso nocturno con reflejos suaves de los componentes."""

    def __init__(self) -> None:
        super().__init__(12.8, 5.1)


class PanelVidrio(Object3D, component=ASSETS / 'panel_vidrio.js'):
    """Vidrio de los depósitos sin escritura de profundidad en WebGL."""

    def __init__(self, ancho: float, fondo: float, alto: float) -> None:
        super().__init__(ancho, fondo, alto)


class TanqueLlenado(Object3D, component=ASSETS / 'tanque_llenado.js'):
    """Reproduce una trayectoria física precalculada y comparte su estado visual."""

    def __init__(self, ancho: float, fondo: float, base: float, inicial: float,
                 nivel: float, salida: float, escena_id: str) -> None:
        super().__init__(ancho, fondo, base, inicial, nivel, salida, escena_id)
        self.trayectoria: list[list[float]] = []
        self.activa = False
        self.pausada = False
        self.revision = None

    def establecer_trayectoria(self, trayectoria: list[list[float]], revision: tuple[int, int],
                               activa: bool, pausada: bool, motivo: str) -> None:
        self.trayectoria, self.revision = trayectoria, revision
        self.activa, self.pausada = activa, pausada
        self.motivo = motivo
        self.run_method('set_trajectory', trayectoria, list(revision), activa, pausada,
                        SEGUNDOS_SIMULADOS_POR_SEGUNDO, motivo)

    def establecer_reproduccion(self, activa: bool, pausada: bool) -> None:
        self.activa, self.pausada = activa, pausada
        self.run_method('set_playback', activa, pausada)

    def _resend(self) -> None:
        super()._resend()
        if self.revision is not None:
            self.run_method('set_trajectory', self.trayectoria, list(self.revision),
                            self.activa, self.pausada, SEGUNDOS_SIMULADOS_POR_SEGUNDO, self.motivo)

    def reproducir(self) -> None:
        self.run_method('restart')


@dataclass(frozen=True)
class Geometria3D:
    """Escala de exposición, no escala métrica de una instalación real."""

    nivel_origen: float
    nivel_destino: float
    x_destino: float
    radio: float
    fraccion_origen: float = .75
    fraccion_destino: float = .125

    @property
    def base_origen(self) -> float:
        return ALTURA_TOMA - .08

    @property
    def maximo_origen(self) -> float:
        return ALTURA_TOMA + ALTURA_VISUAL_AGUA

    @property
    def maximo_destino(self) -> float:
        return self.base_destino + .08 + ALTURA_VISUAL_AGUA

    @property
    def nivel_final_origen(self) -> float:
        # Mantiene bajo el agua toda la sección visible de la entrada de succión.
        return ALTURA_TOMA

    @property
    def descenso_origen(self) -> float:
        return ALTURA_VISUAL_AGUA * self.fraccion_origen

    @property
    def nivel_inicial_destino(self) -> float:
        return self.nivel_destino

    @property
    def entrada_destino(self) -> float:
        # El tubo descarga por encima de la superficie y deja visible el chorro.
        return self.maximo_destino + .16

    @property
    def base_destino(self) -> float:
        return self.nivel_destino - .08 - ALTURA_VISUAL_AGUA * self.fraccion_destino

    @property
    def recorrido(self) -> list[list[float]]:
        puntos = [
            [-4.15, 0.0, 0.58], [-1.95, 0.0, 0.58],
            [0.23, 0.0, 0.58], [1.92, 0.0, 0.58],
        ]
        if self.entrada_destino > .95:
            puntos.extend([
                [2.12, 0.0, .78], [2.12, 0.0, self.entrada_destino - .2],
                [2.32, 0.0, self.entrada_destino],
            ])
        else:
            puntos.append([2.12, 0.0, self.entrada_destino])
        puntos.append([self.x_destino - .52, 0.0, self.entrada_destino])
        return puntos


def geometria_3d(instalacion: Instalacion,
                 tanques: ConfiguracionTanques | None = None) -> Geometria3D:
    """Comprime L, Δz y D visualmente, manteniendo el orden y las cotas relativas."""
    desnivel = 2.45 * math.log1p(instalacion.desnivel_m) / math.log1p(100)
    distancia = 0.42 * math.log1p(instalacion.longitud_m / 10) / math.log1p(100)
    radio = 0.082 + 0.052 * math.log(instalacion.diametro_m / 0.01, 20)
    fraccion_origen = .75 if tanques is None else tanques.origen.inicial_m3 / tanques.origen.capacidad_m3
    fraccion_destino = .125 if tanques is None else tanques.destino.inicial_m3 / tanques.destino.capacidad_m3
    nivel_origen = ALTURA_TOMA + ALTURA_VISUAL_AGUA * fraccion_origen
    return Geometria3D(nivel_origen, nivel_origen + desnivel, 3.9 + distancia, radio,
                       fraccion_origen, fraccion_destino)


def rapidez_3d(velocidad_ms: float) -> float:
    """Escala monótona común a A/B, en unidades visuales por segundo."""
    if not math.isfinite(velocidad_ms) or velocidad_ms < 0:
        raise ValueError('La velocidad debe ser finita y no negativa.')
    return 2.8 * velocidad_ms / (velocidad_ms + 1.8)


class VistaEscena3D:
    """Construye la instalación y sincroniza únicamente el estado hidráulico."""

    def __init__(self, sesion: SesionSimulacion) -> None:
        self.sesion = sesion
        self.geometria: Geometria3D | None = None
        self.particulas: AguaEnTuberia | None = None
        self.agua_destino: TanqueLlenado | None = None
        self.superficies: list[SuperficieAgua] = []
        self.canales: list[CanalAgua] = []
        self.pausada = False
        self.escena_id = uuid4().hex
        self.revision_trayectoria: tuple[int, int] | None = None
        self.trayectoria: TrayectoriaLlenado | None = None
        self.escena = ui.scene(
            width=840, height=470, grid=False, background_color='#080f2b',
            camera=ui.scene.perspective_camera(fov=42), fps=30,
        ).classes('pc-three-canvas').style('width:100%; height:100%;').props(
            'role=img aria-label="Vista 3D de dos depósitos, bomba, tubería y agua que fluye según la velocidad calculada"'
        )
        self.escena.move_camera(0, -13, 5.8, look_at_x=0, look_at_y=0, look_at_z=1.28, duration=0)
        self.actualizar()

    def reiniciar_camara(self) -> None:
        self.escena.move_camera(0, -13, 5.8, look_at_x=0, look_at_y=0, look_at_z=1.28, duration=0.45)

    def reproducir(self) -> None:
        """Vuelve al comienzo de la secuencia visual del escenario vigente."""
        if self.agua_destino is not None:
            self.agua_destino.reproducir()
        for superficie in self.superficies:
            superficie.reproducir()
        if self.particulas is not None:
            self.particulas.reproducir()
        for canal in self.canales:
            canal.reproducir()

    def actualizar(self, pausada: bool = False) -> None:
        self.pausada = pausada
        instalacion = self.sesion.escenario.instalacion if self.sesion.escenario else None
        if instalacion is None:
            # Conservamos la última geometría durante una edición inválida,
            # pero retiramos cualquier indicación de flujo calculado.
            self._sincronizar_flujo()
            return
        nueva = geometria_3d(instalacion, self.sesion.tanques)
        if nueva != self.geometria:
            self.geometria = nueva
            self._construir(nueva)
        self._sincronizar_flujo()

    def _sincronizar_flujo(self) -> None:
        punto = self.sesion.punto_vigente
        valida = punto is not None and punto.caudal_m3s > 0 and self.sesion.tanques is not None
        revision = (self.sesion.revision, self.sesion.revision_tanques)
        calcular = valida and revision != self.revision_trayectoria
        if calcular:
            self.trayectoria = simular_llenado(self.sesion.escenario, self.sesion.tanques)
            self.revision_trayectoria = revision
        activa = bool(valida and self.trayectoria and len(self.trayectoria.estados) > 1)
        rapidez = rapidez_3d(punto.sistema.velocidad_ms) if activa else 0.0
        if self.agua_destino is not None:
            if valida and (calcular or self.agua_destino.revision is None):
                self.agua_destino.establecer_trayectoria(
                    self._fotogramas(self.trayectoria), revision, activa, self.pausada,
                    self.trayectoria.motivo_parada)
            elif self.agua_destino.revision is None:
                g = self.geometria
                tanques = self.sesion.tanques
                origen = tanques.origen.inicial_m3 if tanques else 0
                destino = tanques.destino.inicial_m3 if tanques else 0
                self.agua_destino.establecer_trayectoria(
                    [[0, g.nivel_origen, g.nivel_destino, 0, 0, origen, destino,
                      origen / tanques.origen.area_m2 if tanques else 0,
                      destino / tanques.destino.area_m2 if tanques else 0,
                      self.sesion.escenario.instalacion.desnivel_m
                      if self.sesion.escenario else 0]],
                    revision, False, self.pausada, 'Sin trayectoria vigente')
            else:
                self.agua_destino.establecer_reproduccion(activa, self.pausada)
        if self.particulas is not None:
            self.particulas.establecer_flujo(rapidez, activa, self.pausada)
        for superficie in self.superficies:
            superficie.establecer_flujo(activa, self.pausada)
        for canal in self.canales:
            canal.establecer_flujo(rapidez, activa, self.pausada)

    def _fotogramas(self, trayectoria: TrayectoriaLlenado) -> list[list[float]]:
        g = self.geometria
        tanques = self.sesion.tanques
        inicial_origen = tanques.origen.inicial_m3
        return [[estado.tiempo_s,
                 ALTURA_TOMA + ALTURA_VISUAL_AGUA * estado.origen_m3 / tanques.origen.capacidad_m3,
                 g.base_destino + .08 + ALTURA_VISUAL_AGUA * estado.destino_m3 / tanques.destino.capacidad_m3,
                 rapidez_3d(estado.velocidad_ms), estado.caudal_m3s * 3600,
                 estado.origen_m3, estado.destino_m3,
                 estado.origen_m3 / tanques.origen.area_m2,
                 estado.destino_m3 / tanques.destino.area_m2,
                 self.sesion.escenario.instalacion.desnivel_m
                 + (inicial_origen - estado.origen_m3)
                 * (1 / tanques.origen.area_m2 + 1 / tanques.destino.area_m2)]
                for estado in trayectoria.estados]

    def _construir(self, g: Geometria3D) -> None:
        escena = self.escena
        escena.clear()
        self.superficies = []
        self.canales = []
        self.agua_destino = None

        def caja(ancho: float, fondo: float, alto: float, x: float, y: float, z: float,
                 color: str, opacidad: float = 1) -> None:
            escena.box(ancho, fondo, alto).material(color, opacidad, side='both').move(x, y, z)

        def cilindro_x(x0: float, x1: float, z: float, radio: float, color: str,
                      opacidad: float = 1) -> None:
            if x1 - x0 < 1e-5:
                return
            escena.cylinder(radio, radio, x1 - x0, 24).material(color, opacidad).rotate(0, 0, math.pi / 2).move(
                (x0 + x1) / 2, 0, z)

        def cilindro_z(z0: float, z1: float, x: float, radio: float, color: str,
                      opacidad: float = 1) -> None:
            if z1 - z0 < 1e-5:
                return
            escena.cylinder(radio, radio, z1 - z0, 24).material(color, opacidad).rotate(
                math.pi / 2, 0, 0).move(x, 0, (z0 + z1) / 2)

        def tubo(x0: float, x1: float, z: float) -> None:
            cilindro_x(x0, x1, z, g.radio * 1.48, '#155c7d', .74)
            cilindro_x(x0, x1, z, g.radio, '#20c6e5', .72)
            cilindro_x(x0, x1, z + g.radio * .88, g.radio * .12, '#9cecff', .74)

        def tubo_vertical(z0: float, z1: float, x: float) -> None:
            cilindro_z(z0, z1, x, g.radio * 1.48, '#155c7d', .74)
            cilindro_z(z0, z1, x, g.radio, '#20c6e5', .72)

        def codo(inicio: list[float], control: list[float], fin: list[float]) -> None:
            escena.quadratic_bezier_tube(inicio, control, fin, 30, g.radio * 1.48, 16).material(
                '#155c7d', .74)
            escena.quadratic_bezier_tube(inicio, control, fin, 30, g.radio, 16).material(
                '#20c6e5', .72)

        def tanque(x: float, base: float, nivel: float, *, destino: bool) -> None:
            ancho, fondo = (2.2, 1.5) if destino else (2.05, 1.5)
            altura = ALTURA_VISUAL_AGUA + .34
            # Estructura abierta por ambos lados para que el agua siga visible al girar.
            caja(ancho, fondo, .12, x, 0, base, '#414e74')
            for lado in (-1, 1):
                for profundidad in (-.72, .72):
                    caja(.09, .09, altura, x + lado * ancho / 2, profundidad,
                         base + altura / 2, '#7188aa')
                caja(.12, fondo + .12, .08, x + lado * ancho / 2, 0,
                     base + altura, '#9aafd0')
            for profundidad in (-.72, .72):
                caja(ancho + .1, .09, .07, x, profundidad, base + altura, '#8fa6c5')
            # Paneles de vidrio abiertos arriba; la cara frontal deja leer el nivel.
            for profundidad in (-.71, .71):
                PanelVidrio(ancho - .13, .022, altura - .12).move(
                    x, profundidad, base + altura / 2)
            for lado in (-1, 1):
                PanelVidrio(.022, fondo - .12, altura - .12).move(
                    x + lado * (ancho / 2 - .045), 0, base + altura / 2)
            if destino:
                # El nivel se obtiene del volumen calculado para el destino.
                self.agua_destino = TanqueLlenado(
                    ANCHO_AGUA_DESTINO, FONDO_AGUA, base + .08, g.nivel_destino,
                    g.maximo_destino, g.entrada_destino,
                    self.escena_id,
                )
                self.agua_destino.move(x, 0, 0)
            else:
                superficie = SuperficieAgua(
                    ANCHO_AGUA_ORIGEN, FONDO_AGUA, base + .08, nivel,
                    g.descenso_origen, self.escena_id,
                )
                superficie.move(x, 0, 0)
                self.superficies.append(superficie)

        def etiqueta(texto: str, x: float, inicio: float, fin: float, color: str) -> None:
            escena.line([x, -.36, inicio], [x, -.36, fin - .2]).material(color, .85)
            escena.sphere(.031, 10, 8).material(color).move(x, -.36, inicio)
            escena.text(
                texto,
                style=f'color:{color};font:800 11px "Segoe UI",sans-serif;'
                      'letter-spacing:.025em;white-space:nowrap;text-shadow:0 2px 8px #02091c;'
                      'pointer-events:none;',
            ).move(x, -.36, fin)

        with escena:
            # Suelo oscuro y bases, siguiendo la iluminación de la referencia.
            SueloLuminoso().move(.08, 0, -.045)
            caja(3.0, 2.15, .08, -1.0, 0, .08, '#25254d')
            caja(2.45, 1.9, g.base_origen - .12, -4.05, 0,
                 (g.base_origen + .12) / 2, '#1f2748')
            if g.base_destino > .16:
                caja(2.6, 1.9, g.base_destino - .12, g.x_destino, 0,
                     (g.base_destino + .12) / 2, '#1f2748')
            tanque(-4.05, g.base_origen, g.nivel_origen, destino=False)
            tanque(g.x_destino, g.base_destino, g.nivel_destino, destino=True)

            # Línea de aspiración, bomba y descarga. El diámetro mostrado se comprime visualmente.
            tubo(-4.16, -1.93, .58)
            tubo(.23, 1.92, .58)
            if g.entrada_destino > .95:
                codo([1.92, 0, .58], [2.12, 0, .58], [2.12, 0, .78])
                tubo_vertical(.78, g.entrada_destino - .2, 2.12)
                codo([2.12, 0, g.entrada_destino - .2],
                     [2.12, 0, g.entrada_destino], [2.32, 0, g.entrada_destino])
                tubo(2.32, g.x_destino - .52, g.entrada_destino)
                descarga = [
                    [.23, 0, .58], [1.92, 0, .58], [2.12, 0, .78],
                    [2.12, 0, g.entrada_destino - .2],
                    [2.32, 0, g.entrada_destino], [g.x_destino - .52, 0, g.entrada_destino],
                ]
            else:
                codo([1.92, 0, .58], [2.12, 0, .58], [2.12, 0, g.entrada_destino])
                tubo(2.12, g.x_destino - .52, g.entrada_destino)
                descarga = [
                    [.23, 0, .58], [1.92, 0, .58], [2.12, 0, g.entrada_destino],
                    [g.x_destino - .52, 0, g.entrada_destino],
                ]
            self.canales.append(CanalAgua(
                [[-4.16, 0, .58], [-1.93, 0, .58]], g.radio * .78, self.escena_id))
            self.canales.append(CanalAgua(descarga, g.radio * .78, self.escena_id))

            # Geometría y materiales PBR procedentes del archivo Blender aportado.
            escena.gltf(BOMBA_URL)
            etiqueta('DEPÓSITO DE SUCCIÓN', -4.05, g.nivel_origen + .45, g.nivel_origen + 1.0, '#4beaff')
            etiqueta('BOMBA', -.9, 1.30, 2.16, '#b999ff')
            etiqueta('DEPÓSITO DE DESCARGA', g.x_destino,
                     g.nivel_destino + .45, g.nivel_destino + 1.0, '#4beaff')
            # Discretas luces de acento, sin depender de recursos externos.
            escena.spot_light('#26cbff', intensity=1.4, distance=9, angle=.95, penumbra=.8).move(-4, -3.2, 4.5)
            escena.spot_light('#8965ff', intensity=2.0, distance=8, angle=1.0, penumbra=.7).move(-1, -3, 3.5)
            escena.spot_light('#43dcff', intensity=1.2, distance=8, angle=1.0, penumbra=.8).move(4, -2.8, 5)

            self.particulas = AguaEnTuberia(g.recorrido, g.radio, self.escena_id)
