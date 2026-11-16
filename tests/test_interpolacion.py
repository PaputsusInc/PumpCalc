"""Referencias de interpolación fijadas por las secciones 8 y 9."""

import pytest

from pumpcalc.ejemplos import caso_base
from pumpcalc.entradas import ErrorEntrada, validar_curva
from pumpcalc.interpolacion import altura_bomba


@pytest.mark.parametrize(('q_m3h', 'h_m'), [
    (0, 35), (1, 34), (2, 31), (3, 26), (4, 19), (5, 10),
])
def test_reproduce_todos_los_nodos_incluidos_extremos(q_m3h, h_m):
    assert altura_bomba(caso_base().curva, q_m3h / 3600) == h_m


@pytest.mark.parametrize(('q_m3h', 'h_m'), [
    (0.5, 34.5), (1.5, 32.5), (2.5, 28.5), (3.5, 22.5), (4.5, 14.5),
])
def test_interpolacion_en_cada_tramo(q_m3h, h_m):
    assert altura_bomba(caso_base().curva, q_m3h / 3600) == pytest.approx(h_m)


@pytest.mark.parametrize('q_m3h', [-0.001, 5.001, float('nan'), float('inf')])
def test_no_extrapola_ni_acepta_caudales_no_finitos(q_m3h):
    with pytest.raises(ErrorEntrada) as error:
        altura_bomba(caso_base().curva, q_m3h / 3600)
    assert error.value.campo == 'caudal_m3s'


def test_dominio_inicial_positivo_y_tramo_horizontal():
    curva = validar_curva([(1, 10), (2, 10), (4, 0)])
    assert altura_bomba(curva, 1 / 3600) == 10
    assert altura_bomba(curva, 1.5 / 3600) == 10
    assert altura_bomba(curva, 3 / 3600) == pytest.approx(5)
    assert altura_bomba(curva, 4 / 3600) == 0
    with pytest.raises(ErrorEntrada):
        altura_bomba(curva, 0)
