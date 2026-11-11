"""Geometría y movimiento ilustrativos del flujo, calculados en Python."""

import base64
from dataclasses import dataclass
from html import escape
import math

from pumpcalc.entradas import Instalacion
from pumpcalc.operacion import ResultadoOperacion


ANCHO_ESCENA = 840
ALTO_ESCENA = 380
NIVEL_ORIGEN_Y = 212.0
NUMERO_TRAZAS = 16


def rapidez_visual(velocidad_ms: float) -> float:
    """Escala común A/B en píxeles por segundo; v se introduce en m/s."""
    if not math.isfinite(velocidad_ms) or velocidad_ms < 0:
        raise ValueError('La velocidad debe ser finita y no negativa.')
    return 240 * (velocidad_ms / (velocidad_ms + 2))


def grosor_tuberia(diametro_m: float) -> float:
    """Escala visual creciente en el dominio, sin escala geométrica real."""
    if not math.isfinite(diametro_m) or not 0.01 <= diametro_m <= 0.2:
        raise ValueError('El diámetro debe estar entre 0,01 y 0,2 m.')
    return 8 + 12 * math.log2(diametro_m / 0.01)


@dataclass(frozen=True)
class Trayecto:
    """Centro de la tubería que comparten el SVG y las trazas en movimiento."""

    deposito_x: float
    nivel_destino_y: float

    @property
    def puntos(self) -> tuple[tuple[float, float], ...]:
        codo_x = self.deposito_x - 92
        salida_y = self.nivel_destino_y + 53
        return ((150, 265), (codo_x, 265), (codo_x, salida_y),
                (self.deposito_x + 30, salida_y))

    @property
    def longitud_px(self) -> float:
        inicio, *_, destino = self.puntos
        return destino[0] - inicio[0] + abs(destino[1] - inicio[1])

    def posicion(self, distancia_px: float) -> tuple[float, float]:
        """Convierte una distancia acumulada en coordenadas del tramo recorrido."""
        if not math.isfinite(distancia_px):
            raise ValueError('La posición de la traza debe ser finita.')
        restante = distancia_px % self.longitud_px
        puntos = self.puntos
        for (x0, y0), (x1, y1) in zip(puntos, puntos[1:]):
            longitud = math.hypot(x1 - x0, y1 - y0)
            if longitud == 0:  # Depósitos a la misma altura.
                continue
            if restante <= longitud:
                t = restante / longitud
                return x0 + t * (x1 - x0), y0 + t * (y1 - y0)
            restante -= longitud
        return puntos[-1]


def trayecto_instalacion(instalacion: Instalacion) -> Trayecto:
    """Comprime los rangos de L y Δz para mantener la instalación en pantalla."""
    x = 515 + 160 * math.log1p(instalacion.longitud_m / 10) / math.log1p(100)
    elevacion = 150 * math.log1p(instalacion.desnivel_m / 3) / math.log1p(100 / 3)
    return Trayecto(round(x, 3), round(NIVEL_ORIGEN_Y - elevacion, 3))


TRAYECTO_INICIAL = Trayecto(571, 144)


@dataclass
class MovimientoFlujo:
    fase_px: float = 0.0
    pausada: bool = False
    velocidad_ms: float | None = None
    trayecto: Trayecto = TRAYECTO_INICIAL

    def sincronizar(self, estado: str, resultado: ResultadoOperacion | None) -> None:
        """Usa la velocidad del punto vigente y suspende el avance si falta."""
        if (estado == 'solucion' and resultado is not None
                and resultado.estado == 'solucion' and resultado.punto is not None):
            self.velocidad_ms = resultado.punto.sistema.velocidad_ms
        else:
            self.velocidad_ms = None

    @property
    def rapidez_px_s(self) -> float:
        return 0 if self.pausada or self.velocidad_ms is None else rapidez_visual(self.velocidad_ms)

    def avanzar(self, segundos: float) -> bool:
        """Avanza según el tiempo real y devuelve si hay que redibujar."""
        if not math.isfinite(segundos) or segundos < 0:
            raise ValueError('El tiempo entre fotogramas debe ser finito y no negativo.')
        rapidez = self.rapidez_px_s
        if rapidez == 0 or segundos == 0:
            return False
        self.fase_px = (self.fase_px + rapidez * segundos) % self.trayecto.longitud_px
        return True


def capa_trazas(fase_px: float, grosor_px: float, trayecto: Trayecto) -> str:
    """Solo la capa móvil: no incluye instalación, etiquetas ni cálculos."""
    radio = min(3.5, max(1.7, grosor_px * 0.1))
    circulos = []
    for indice in range(NUMERO_TRAZAS):
        x, y = trayecto.posicion(fase_px + indice * trayecto.longitud_px / NUMERO_TRAZAS)
        circulos.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radio:.2f}"/>')
    return '<g fill="#d5fa55" stroke="#f8ffda" stroke-width="0.6">' + ''.join(circulos) + '</g>'


def fondo_instalacion(instalacion: Instalacion | None,
                      resultado: ResultadoOperacion | None,
                      trayecto: Trayecto) -> str:
    """SVG estático. Los depósitos mantienen niveles fijos en cada escenario."""
    grosor = grosor_tuberia(instalacion.diametro_m) if instalacion is not None else 24
    punto = resultado.punto if resultado is not None and resultado.estado == 'solucion' else None

    def dato(valor: float, decimales: int = 2) -> str:
        return f'{valor:.{decimales}f}'.replace('.', ',')

    longitud = '—' if instalacion is None else dato(instalacion.longitud_m)
    diametro = '—' if instalacion is None else dato(instalacion.diametro_m * 1000)
    desnivel = '—' if instalacion is None else dato(instalacion.desnivel_m)
    rugosidad = '—' if instalacion is None else f'{instalacion.rugosidad_m * 1000:.6g}'.replace('.', ',')
    k_total = '—' if instalacion is None else dato(instalacion.k_total)
    perdida_tuberia = '—' if punto is None else dato(punto.sistema.perdida_tuberia_m, 3)
    perdida_accesorios = '—' if punto is None else dato(punto.sistema.perdida_accesorios_m, 3)
    caudal = '—' if punto is None else dato(punto.caudal_m3s * 3600, 6)
    velocidad = '—' if punto is None else dato(punto.sistema.velocidad_ms, 6)
    texto = escape(f'Q = {caudal} m³/h     v = {velocidad} m/s')
    x = trayecto.deposito_x
    y = trayecto.nivel_destino_y
    (inicio_x, inicio_y), (codo_x, _), _, (salida_x, salida_y) = trayecto.puntos
    tuberia = f'M{inicio_x} {inicio_y} H{codo_x:.3f} V{salida_y:.3f} H{salida_x:.3f}'
    desnivel_svg = ''
    if y < NIVEL_ORIGEN_Y:
        marca_x = x + 144
        desnivel_svg = (
            f'<path d="M{marca_x} {y} V{NIVEL_ORIGEN_Y} '
            f'M{marca_x - 6} {y} H{marca_x + 6} '
            f'M{marca_x - 6} {NIVEL_ORIGEN_Y} H{marca_x + 6}" '
            'stroke="#6da4b5" stroke-width="1.5"/>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="840" height="380" viewBox="0 0 840 380">
<defs>
<pattern id="rejilla" width="28" height="28" patternUnits="userSpaceOnUse">
<path d="M28 0 H0 V28" fill="none" stroke="#224b59" stroke-width="0.6"/>
</pattern>
<linearGradient id="agua" x1="0" y1="0" x2="0" y2="1">
<stop offset="0" stop-color="#29d9d0" stop-opacity="0.7"/>
<stop offset="1" stop-color="#0a8498" stop-opacity="0.35"/>
</linearGradient>
</defs>
<rect width="840" height="380" rx="12" fill="#092c3b"/>
<rect width="840" height="380" rx="12" fill="url(#rejilla)"/>
<g font-family="Segoe UI, Arial, sans-serif" font-size="15" fill="#c5e7ed">
<text x="36" y="41" fill="#8ef5e7">Rugosidad ε = {rugosidad} mm · Pérdida en tubería: {perdida_tuberia} m</text>
<text x="36" y="67" fill="#8ef5e7">Accesorios K = {k_total} · Pérdida localizada: {perdida_accesorios} m</text>
<text x="36" y="112">Depósito de origen</text>
<rect x="40" y="212" width="128" height="112" fill="url(#agua)"/>
<path d="M38 128 V326 H170 V128" fill="none" stroke="#72b3c0" stroke-width="3"/>
<path d="M40 212 H168" stroke="#55e7df" stroke-width="2"/>
<text x="48" y="201" font-size="12" fill="#8fb8c5">Nivel fijo</text>
<text x="{x - 3}" y="{max(18, y - 52)}">Depósito de destino</text>
<rect id="agua-destino" x="{x + 2}" y="{y}" width="128" height="103" fill="url(#agua)"/>
<path d="M{x} {y - 43} V{y + 105} H{x + 132} V{y - 43}" fill="none" stroke="#72b3c0" stroke-width="3"/>
<path d="M{x + 2} {y} H{x + 130}" stroke="#55e7df" stroke-width="2"/>
<text x="{x + 15}" y="{y - 10}" font-size="12" fill="#8fb8c5">Nivel fijo</text>
<path d="{tuberia}" fill="none" stroke="#041c29" stroke-width="{grosor + 12:.3f}" stroke-linejoin="round" transform="translate(0 5)"/>
<path d="{tuberia}" fill="none" stroke="#398696" stroke-width="{grosor + 6:.3f}" stroke-linejoin="round"/>
<path id="tuberia" d="{tuberia}" fill="none" stroke="#0d7186" stroke-width="{grosor:.3f}" stroke-linejoin="round"/>
<circle cx="278" cy="265" r="43" fill="#0a3442" stroke="#315a66" stroke-width="1"/>
<circle cx="278" cy="265" r="34" fill="#d5fa55" stroke="#edff9e" stroke-width="2"/>
<path d="M262 251 Q288 244 293 264 Q284 280 264 276" fill="none" stroke="#173b3b" stroke-width="4"/>
<circle cx="278" cy="265" r="5" fill="#173b3b"/>
<text x="249" y="326" font-size="13" fill="#d5fa55">Bomba</text>
<text x="361" y="322" font-size="14">L = {longitud} m</text>
<text x="352" y="223" font-size="14">D = {diametro} mm</text>
{desnivel_svg}
<text x="{x + 4}" y="{y + 120}" font-size="14">Δz = {desnivel} m</text>
<path d="M36 337 H804" stroke="#315462" stroke-width="1"/>
<text x="36" y="362" font-size="16" fill="#8ef5e7">{texto}</text>
<text x="584" y="362" font-size="11" fill="#8fb8c5">Esquema sin escala geométrica</text>
</g></svg>'''


def fuente_svg(svg: str) -> str:
    return 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode('utf-8')).decode('ascii')
