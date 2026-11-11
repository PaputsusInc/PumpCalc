"""Datos ficticios de la sección 8 de la línea base; no son mediciones."""

from dataclasses import replace

from pumpcalc.entradas import Escenario, validar_curva, validar_instalacion, validar_objetivo


CURVA_DEMOSTRACION = ((0, 35), (1, 34), (2, 31), (3, 26), (4, 19), (5, 10))
OBJETIVO_DEMOSTRACION_M3H = 4
EJEMPLOS = {'base': 'Caso base', 'diametro32': 'Diámetro de 32 mm', 'sin_interseccion': 'Sin intersección'}


def caso_base() -> Escenario:
    """Construye una configuración independiente en las unidades del motor."""
    return Escenario(
        instalacion=validar_instalacion(
            longitud_m=40, diametro_mm=25, desnivel_m=12,
            rugosidad_mm=0.0015, k_total=4,
        ),
        curva=validar_curva(CURVA_DEMOSTRACION),
    )


def objetivo_demostracion_m3s() -> float:
    return validar_objetivo(OBJETIVO_DEMOSTRACION_M3H)


def escenario_ejemplo(nombre: str) -> Escenario:
    base = caso_base()
    if nombre == 'base':
        return base
    if nombre == 'diametro32':
        return replace(base, instalacion=replace(base.instalacion, diametro_m=0.032))
    if nombre == 'sin_interseccion':
        return replace(base, instalacion=replace(base.instalacion, desnivel_m=40))
    raise ValueError('Ejemplo desconocido.')
