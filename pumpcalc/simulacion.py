"""Estado de un formulario de simulación, independiente de los controles UI."""

from pumpcalc.ejemplos import CURVA_DEMOSTRACION, caso_base
from pumpcalc.entradas import ErrorEntrada, Escenario, validar_curva, validar_instalacion
from pumpcalc.operacion import ResultadoOperacion, resolver_operacion


class SesionSimulacion:
    def __init__(self) -> None:
        self.revision = 0
        self.resultado: ResultadoOperacion | None = None
        self.escenario: Escenario | None = None
        self.error: ErrorEntrada | None = None
        self.estado = 'pendiente'
        self.cargar_base()

    def cargar_base(self) -> None:
        instalacion = caso_base().instalacion
        self.entradas = {
            'longitud_m': f'{instalacion.longitud_m:g}',
            'diametro_mm': f'{instalacion.diametro_m * 1000:g}',
            'desnivel_m': f'{instalacion.desnivel_m:g}',
            'rugosidad_mm': f'{instalacion.rugosidad_m * 1000:g}',
            'k_total': f'{instalacion.k_total:g}',
        }
        self.puntos = [[str(q), str(h)] for q, h in CURVA_DEMOSTRACION]
        self.preparar()

    def preparar(self) -> None:
        """Retira inmediatamente cualquier resultado de las entradas anteriores."""
        self.revision += 1
        self.resultado = None
        self.escenario = None
        self.error = None
        try:
            instalacion = validar_instalacion(**self.entradas)
            curva = validar_curva(self.puntos)
            self.escenario = Escenario(instalacion, curva)
            self.estado = 'pendiente'
        except ErrorEntrada as error:
            self.estado = 'datos_invalidos'
            self.error = error

    def editar_instalacion(self, campo: str, valor: str) -> None:
        if campo not in self.entradas:
            raise KeyError(campo)
        self.entradas[campo] = valor
        self.preparar()

    def editar_punto(self, indice: int, columna: int, valor: str) -> None:
        self.puntos[indice][columna] = valor
        self.preparar()

    def agregar_punto(self) -> bool:
        if len(self.puntos) >= 10:
            return False
        self.puntos.append(['', ''])
        self.preparar()
        return True

    def quitar_punto(self, indice: int) -> bool:
        if len(self.puntos) <= 3:
            return False
        self.puntos.pop(indice)
        self.preparar()
        return True

    def simular(self) -> None:
        self.preparar()
        if self.escenario is not None:
            self.resultado = resolver_operacion(self.escenario)
            self.estado = self.resultado.estado

    def simular_revision(self, revision: int) -> bool:
        """Una llamada diferida antigua no puede publicar un resultado vigente."""
        if revision != self.revision or self.estado != 'pendiente':
            return False
        self.simular()
        return True
