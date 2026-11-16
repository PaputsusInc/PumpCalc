"""Referencias y continuidad del factor de Darcy de la línea base."""

import math

import pytest

from pumpcalc.entradas import ErrorEntrada
from pumpcalc.friccion import ErrorConvergencia, colebrook, factor_friccion


def test_laminar_y_caudal_cero_no_requieren_colebrook(monkeypatch):
    def no_debe_ejecutarse(*args, **kwargs):
        raise AssertionError('Colebrook no aplica a este régimen.')

    monkeypatch.setattr('pumpcalc.friccion.colebrook', no_debe_ejecutarse)
    cero = factor_friccion(0, 0.0001)
    assert cero.factor_darcy is None
    assert cero.regimen == 'sin_flujo'
    assert cero.colebrook is None
    laminar = factor_friccion(1000, 0.0001)
    assert laminar.factor_darcy == 0.064
    assert laminar.regimen == 'laminar'
    assert laminar.colebrook is None
    assert factor_friccion(2000, 0.05).factor_darcy == 0.032


def test_referencia_turbulenta_y_residuo_independiente():
    resultado = colebrook(100000, 0.0001)
    assert resultado.factor_darcy == pytest.approx(0.018513866077, abs=1e-9, rel=0)
    ultimo = resultado.traza[-1]
    residuo = ultimo.x + 2 * math.log10(0.0001 / 3.7 + 2.51 * ultimo.x / 100000)
    assert abs(residuo) <= 1e-10
    assert ultimo.cambio <= 1e-10
    assert resultado.iteraciones == ultimo.iteracion <= 100


def test_parada_exige_cambio_y_residuo_simultaneamente():
    resultado = colebrook(100000, 0.0001, tolerancia=0.1)
    primero = resultado.traza[0]
    assert abs(primero.residuo) < 0.1 < primero.cambio
    assert resultado.iteraciones > 1
    assert resultado.traza[-1].cambio <= 0.1
    assert abs(resultado.traza[-1].residuo) <= 0.1


@pytest.mark.parametrize('reynolds', [4000, 4 * (100 / 3600) / (math.pi * 0.01 * 1.004e-6)])
@pytest.mark.parametrize('rugosidad', [0, 0.05])
def test_colebrook_converge_en_extremos_del_dominio(reynolds, rugosidad):
    resultado = colebrook(reynolds, rugosidad)
    assert math.isfinite(resultado.factor_darcy) and resultado.factor_darcy > 0
    assert resultado.iteraciones <= 100
    assert all(3 <= paso.x <= 20 and 3 <= paso.x_anterior <= 20 for paso in resultado.traza)
    assert resultado.traza[-1].cambio <= 1e-10
    assert abs(resultado.traza[-1].residuo) <= 1e-10


@pytest.mark.parametrize('rugosidad', [0, 0.0001, 0.05])
@pytest.mark.parametrize('frontera', [2000, 4000])
def test_continuidad_del_factor_en_ambas_fronteras(frontera, rugosidad):
    centro = factor_friccion(frontera, rugosidad).factor_darcy
    for re in (frontera - 1e-6, frontera + 1e-6):
        assert factor_friccion(re, rugosidad).factor_darcy == pytest.approx(centro, abs=1e-9, rel=0)


def test_transicion_es_interpolacion_didactica_con_traza_auxiliar():
    resultado = factor_friccion(3000, 0.0001)
    f4000 = colebrook(4000, 0.0001).factor_darcy
    assert resultado.factor_darcy == pytest.approx((0.032 + f4000) / 2)
    assert resultado.regimen == 'transicion'
    assert resultado.colebrook.reynolds == 4000
    assert 'didáctica' in resultado.advertencia
    assert 'f₄₀₀₀' in resultado.advertencia
    turbulento = factor_friccion(4000, 0.0001)
    assert turbulento.regimen == 'turbulento'
    assert turbulento.advertencia is None


@pytest.mark.parametrize('reynolds', [3000, 100000])
def test_falta_de_convergencia_se_informa_en_transicion_y_turbulencia(reynolds):
    with pytest.raises(ErrorConvergencia, match='no convergió') as error:
        factor_friccion(reynolds, 0.0001, max_iteraciones=1)
    assert len(error.value.traza) == 1


@pytest.mark.parametrize(('reynolds', 'rugosidad'), [
    (-1, 0), (float('nan'), 0), (float('inf'), 0),
    (100000, -0.001), (100000, 0.05001), (100000, float('nan')),
])
def test_rechaza_datos_fuera_del_dominio(reynolds, rugosidad):
    with pytest.raises(ErrorEntrada):
        factor_friccion(reynolds, rugosidad)


def test_colebrook_directo_exige_reynolds_turbulento():
    with pytest.raises(ErrorEntrada):
        colebrook(3999, 0.0001)


@pytest.mark.parametrize('maximo', [0, -1, 1.5, True])
def test_limite_de_iteraciones_debe_ser_entero_positivo(maximo):
    with pytest.raises(ValueError):
        colebrook(100000, 0.0001, max_iteraciones=maximo)


@pytest.mark.parametrize('tolerancia', [0, -1, float('nan'), float('inf')])
def test_tolerancia_debe_ser_finita_y_positiva(tolerancia):
    with pytest.raises(ValueError):
        colebrook(100000, 0.0001, tolerancia=tolerancia)
