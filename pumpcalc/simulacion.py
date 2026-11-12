"""Estado de un formulario de simulación, independiente de los controles UI."""

from copy import deepcopy

from pumpcalc.ejemplos import caso_base
from pumpcalc.entradas import ErrorEntrada, Escenario, numero_decimal, validar_curva, validar_instalacion
from pumpcalc.operacion import PuntoOperacion, ResultadoOperacion, resolver_operacion


class SesionSimulacion:
    """Conserva el borrador del formulario y el resultado de su revisión vigente."""

    def __init__(self) -> None:
        self.revision = 0
        self.resultado: ResultadoOperacion | None = None
        self.escenario: Escenario | None = None
        self.error: ErrorEntrada | None = None
        self.estado = 'pendiente'
        self.cargar_base()

    @property
    def punto_vigente(self) -> PuntoOperacion | None:
        """Expone el punto solo si pertenece a la revisión que está en pantalla."""
        if self.estado == 'solucion' and self.resultado is not None:
            return self.resultado.punto
        return None

    def cargar_base(self) -> None:
        self.cargar_escenario(caso_base())

    def cargar_escenario(self, escenario: Escenario) -> None:
        instalacion = escenario.instalacion
        # Datos descriptivos del escenario: no sustituyen la curva Q-H.
        self.datos_bomba = {
            'potencia_hp': '',
            'altura_maxima_m': '',
            'caudal_maximo_m3h': '',
        }
        self.errores_datos_bomba: dict[str, str] = {}
        self.entradas = {
            'longitud_m': f'{instalacion.longitud_m:g}',
            'diametro_mm': f'{instalacion.diametro_m * 1000:g}',
            'desnivel_m': f'{instalacion.desnivel_m:g}',
            'rugosidad_mm': f'{instalacion.rugosidad_m * 1000:g}',
            'k_total': f'{instalacion.k_total:g}',
        }
        self.puntos = [[f'{p.caudal_m3s * 3600:.12g}', f'{p.altura_m:.12g}']
                       for p in escenario.curva.puntos]
        self.preparar()

    def copiar(self) -> 'SesionSimulacion':
        """Crea un escenario editable con sus propias filas de la curva."""
        copia = SesionSimulacion()
        copia.entradas = self.entradas.copy()
        copia.datos_bomba = self.datos_bomba.copy()
        copia.errores_datos_bomba = self.errores_datos_bomba.copy()
        copia.puntos = [fila.copy() for fila in self.puntos]
        copia.preparar()
        if self.resultado is not None:
            copia.resultado = deepcopy(self.resultado)
            copia.estado = self.estado
        return copia

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
        self._revisar_datos_bomba()

    def editar_instalacion(self, campo: str, valor: str) -> None:
        if campo not in self.entradas:
            raise KeyError(campo)
        self.entradas[campo] = valor
        self.preparar()

    def editar_dato_bomba(self, campo: str, valor: str) -> None:
        """Guarda una referencia opcional sin alterar el cálculo hidráulico."""
        if campo not in self.datos_bomba:
            raise KeyError(campo)
        self.datos_bomba[campo] = valor
        self._revisar_datos_bomba()

    def _revisar_datos_bomba(self) -> None:
        """Señala valores imposibles sin usarlos para alterar la curva o el resultado."""
        self.errores_datos_bomba.clear()
        for campo, texto in self.datos_bomba.items():
            if not texto.strip():
                continue
            try:
                valor = numero_decimal(texto, campo)
            except ErrorEntrada as error:
                self.errores_datos_bomba[campo] = str(error)
                continue
            if valor <= 0:
                self.errores_datos_bomba[campo] = 'Introduce un número mayor que cero.'
            elif self.escenario is not None and campo == 'altura_maxima_m':
                if valor < max(p.altura_m for p in self.escenario.curva.puntos):
                    self.errores_datos_bomba[campo] = 'Hmax no puede ser menor que una altura de la curva.'
            elif self.escenario is not None and campo == 'caudal_maximo_m3h':
                if valor < self.escenario.curva.puntos[-1].caudal_m3s * 3600 - 1e-9:
                    self.errores_datos_bomba[campo] = 'Qmax no puede ser menor que un caudal de la curva.'

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
