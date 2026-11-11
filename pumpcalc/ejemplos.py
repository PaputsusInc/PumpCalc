"""Datos ficticios de la sección 8 de la línea base; no son mediciones."""

from pumpcalc.entradas import Escenario, validar_curva, validar_instalacion, validar_objetivo


CURVA_DEMOSTRACION = ((0, 35), (1, 34), (2, 31), (3, 26), (4, 19), (5, 10))
OBJETIVO_DEMOSTRACION_M3H = 4


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
