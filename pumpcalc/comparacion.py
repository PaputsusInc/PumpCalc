"""Dos escenarios en memoria y evaluación de una meta común, sin UI."""

from dataclasses import dataclass

from pumpcalc.ejemplos import OBJETIVO_DEMOSTRACION_M3H, escenario_ejemplo
from pumpcalc.entradas import ErrorEntrada, validar_objetivo
from pumpcalc.simulacion import SesionSimulacion


MENSAJES_META = {
    'sin_meta': 'Sin meta de caudal', 'meta_invalida': 'Meta de caudal inválida',
    'sin_resultado': 'Sin resultado vigente para evaluar la meta',
    'en_limite': 'En el límite numérico',
    'alcanza': 'Alcanza la meta en el modelo',
    'no_alcanza': 'No alcanza la meta en el modelo',
}


@dataclass(frozen=True)
class EvaluacionMeta:
    estado: str
    margen_m3s: float | None = None


@dataclass(frozen=True)
class DiferenciaCaudal:
    cambio_m3s: float
    diferencia_absoluta_m3s: float
    porcentaje: float | None


class ComparacionEscenarios:
    """Agrupa las sesiones A y B y compara ambas contra la misma meta."""

    def __init__(self) -> None:
        self.sesiones = {'A': SesionSimulacion(), 'B': SesionSimulacion()}
        for sesion in self.sesiones.values():
            sesion.simular()
        self.activo = 'A'
        self.comparando = False
        self.objetivo_texto = str(OBJETIVO_DEMOSTRACION_M3H)
        self.objetivo_m3s = validar_objetivo(self.objetivo_texto)
        self.error_objetivo: ErrorEntrada | None = None

    def seleccionar(self, nombre: str) -> None:
        if nombre not in self.sesiones:
            raise ValueError('Selecciona A o B.')
        self.activo = nombre

    def copiar_a_b(self) -> None:
        self.sesiones['B'] = self.sesiones['A'].copiar()

    def cargar_ejemplo(self, nombre: str) -> None:
        sesion = self.sesiones[self.activo]
        sesion.cargar_escenario(escenario_ejemplo(nombre))
        sesion.simular()

    def establecer_objetivo(self, texto: str) -> None:
        """Valida la meta para evaluar el resultado que ya calculó el motor."""
        self.objetivo_texto = texto
        self.error_objetivo = None
        try:
            self.objetivo_m3s = validar_objetivo(texto)
        except ErrorEntrada as error:
            self.objetivo_m3s = None
            self.error_objetivo = error

    def evaluar_meta(self, nombre: str) -> EvaluacionMeta:
        if self.error_objetivo is not None:
            return EvaluacionMeta('meta_invalida')
        if self.objetivo_m3s is None:
            return EvaluacionMeta('sin_meta')
        sesion = self.sesiones[nombre]
        punto = sesion.punto_vigente
        if punto is None:
            return EvaluacionMeta('sin_resultado')
        margen = punto.caudal_m3s - self.objetivo_m3s
        # Se usa la cota de la raíz calculada, no un umbral físico de la instalación.
        if abs(margen) <= sesion.resultado.biseccion.cota_error:
            return EvaluacionMeta('en_limite', margen)
        return EvaluacionMeta('alcanza' if margen > 0 else 'no_alcanza', margen)

    def diferencia_caudal(self) -> DiferenciaCaudal | None:
        punto_a = self.sesiones['A'].punto_vigente
        punto_b = self.sesiones['B'].punto_vigente
        if punto_a is None or punto_b is None:
            return None
        caudal_a = punto_a.caudal_m3s
        cambio = punto_b.caudal_m3s - caudal_a
        porcentaje = None if caudal_a == 0 else 100 * cambio / caudal_a
        return DiferenciaCaudal(cambio, abs(cambio), porcentaje)
