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
        resultado = sesion.resultado
        if sesion.estado != 'solucion' or resultado is None or resultado.punto is None:
            return EvaluacionMeta('sin_resultado')
        margen = resultado.punto.caudal_m3s - self.objetivo_m3s
        if abs(margen) <= resultado.biseccion.cota_error:
            return EvaluacionMeta('en_limite', margen)
        return EvaluacionMeta('alcanza' if margen > 0 else 'no_alcanza', margen)

    def diferencia_caudal(self) -> DiferenciaCaudal | None:
        caudales = []
        for sesion in self.sesiones.values():
            if sesion.estado != 'solucion' or sesion.resultado is None or sesion.resultado.punto is None:
                return None
            caudales.append(sesion.resultado.punto.caudal_m3s)
        a, b = caudales
        cambio = b - a
        return DiferenciaCaudal(cambio, abs(cambio), None if a == 0 else 100 * cambio / a)
