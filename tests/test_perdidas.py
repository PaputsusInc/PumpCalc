"""Balance de alturas, casos límite y referencias de pérdidas en SI."""

from dataclasses import replace
import math

import pytest

from pumpcalc.ejemplos import caso_base
from pumpcalc.entradas import ErrorEntrada
from pumpcalc.friccion import ErrorConvergencia
from pumpcalc.perdidas import evaluar_sistema


def test_caudal_cero_devuelve_altura_estatica_sin_evaluar_friccion(monkeypatch):
    def no_debe_ejecutarse(*args, **kwargs):
        raise AssertionError('No se debe dividir entre Reynolds en Q = 0.')

    monkeypatch.setattr('pumpcalc.perdidas.factor_friccion', no_debe_ejecutarse)
    resultado = evaluar_sistema(caso_base().instalacion, 0)
    assert resultado.area_m2 == pytest.approx(math.pi * 0.025 ** 2 / 4)
    assert resultado.velocidad_ms == resultado.reynolds == 0
    assert resultado.perdida_tuberia_m == resultado.perdida_accesorios_m == 0
    assert resultado.altura_sistema_m == 12
    assert resultado.friccion.factor_darcy is None
    assert resultado.friccion.regimen == 'sin_flujo'


def test_perdidas_en_el_caudal_de_referencia_sin_resolver_aun_el_cruce():
    # Q proviene de la sección 8; este paso evalúa Hs(Q), no busca la raíz.
    resultado = evaluar_sistema(caso_base().instalacion, 3.765443 / 3600)
    assert resultado.velocidad_ms == pytest.approx(2.130805, abs=1e-6, rel=0)
    # Reynolds se da de forma aproximada en la fuente y Q está redondeado.
    assert resultado.reynolds == pytest.approx(53057.90, abs=0.02, rel=0)
    assert resultado.friccion.factor_darcy == pytest.approx(0.020839985, abs=1e-7, rel=0)
    assert resultado.perdida_tuberia_m == pytest.approx(7.716242, abs=1e-5, rel=0)
    assert resultado.perdida_accesorios_m == pytest.approx(0.925654, abs=1e-6, rel=0)
    assert resultado.altura_sistema_m == pytest.approx(20.641896, abs=1e-5, rel=0)
    assert resultado.friccion.regimen == 'turbulento'


def test_perdida_laminar_coincide_con_poiseuille():
    instalacion = caso_base().instalacion
    diametro = 0.025
    velocidad = 1000 * 1.004e-6 / diametro
    q = velocidad * math.pi * diametro ** 2 / 4
    resultado = evaluar_sistema(instalacion, q)
    esperado = 32 * 1.004e-6 * 40 * velocidad / (9.81 * diametro ** 2)
    assert resultado.perdida_tuberia_m == pytest.approx(esperado)
    assert resultado.friccion.factor_darcy == pytest.approx(0.064)
    assert resultado.friccion.colebrook is None


@pytest.mark.parametrize('frontera', [2000, 4000])
def test_continuidad_de_altura_en_los_limites_de_regimen(frontera):
    instalacion = caso_base().instalacion
    q_por_re = 1.004e-6 * math.pi * instalacion.diametro_m / 4
    centro = evaluar_sistema(instalacion, frontera * q_por_re).altura_sistema_m
    for re in (frontera - 1e-6, frontera + 1e-6):
        assert evaluar_sistema(instalacion, re * q_por_re).altura_sistema_m == pytest.approx(
            centro, abs=1e-8, rel=0,
        )


def test_longitud_y_k_participan_sin_coeficientes_ocultos():
    instalacion = caso_base().instalacion
    q = 3 / 3600
    base = evaluar_sistema(instalacion, q)
    largo = evaluar_sistema(replace(instalacion, longitud_m=80), q)
    assert largo.perdida_tuberia_m == pytest.approx(2 * base.perdida_tuberia_m)
    assert largo.perdida_accesorios_m == base.perdida_accesorios_m
    sin_k = evaluar_sistema(replace(instalacion, k_total=0), q)
    assert sin_k.perdida_accesorios_m == 0
    assert sin_k.altura_sistema_m == instalacion.desnivel_m + sin_k.perdida_tuberia_m


def test_rugosidad_y_diametro_cambian_las_perdidas():
    instalacion = caso_base().instalacion
    base = evaluar_sistema(instalacion, 3 / 3600)
    rugoso = evaluar_sistema(replace(instalacion, rugosidad_m=0.0005), 3 / 3600)
    ancho = evaluar_sistema(replace(instalacion, diametro_m=0.032), 3 / 3600)
    assert rugoso.perdida_tuberia_m > base.perdida_tuberia_m
    assert ancho.perdida_tuberia_m < base.perdida_tuberia_m
    assert ancho.velocidad_ms < base.velocidad_ms


def test_fallo_de_colebrook_se_propaga_en_lugar_de_devolver_resultado():
    with pytest.raises(ErrorConvergencia):
        evaluar_sistema(caso_base().instalacion, 3 / 3600, max_iteraciones_colebrook=1)


@pytest.mark.parametrize('caudal', [-0.001, 100.001 / 3600, float('nan'), float('inf')])
def test_rechaza_caudales_fuera_del_sandbox(caudal):
    with pytest.raises(ErrorEntrada) as error:
        evaluar_sistema(caso_base().instalacion, caudal)
    assert error.value.campo == 'caudal_m3s'


def test_caudal_maximo_del_sandbox_produce_resultado_finito():
    resultado = evaluar_sistema(caso_base().instalacion, 100 / 3600)
    assert math.isfinite(resultado.altura_sistema_m)
    assert resultado.friccion.colebrook.iteraciones <= 100
