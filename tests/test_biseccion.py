"""Pruebas matemáticas del solver, independientes del modelo hidráulico."""

import math

import pytest

from pumpcalc.biseccion import ParametrosBiseccion, biseccion


def test_raiz_analitica_y_cota_con_ambas_tolerancias():
    parametros = ParametrosBiseccion(tolerancia_x=1e-6, tolerancia_f=1e-6)
    resultado = biseccion(lambda q: 20 - 2 * q - q ** 2, 0, 5, parametros=parametros)
    exacta = math.sqrt(21) - 1
    assert resultado.estado == 'solucion'
    assert resultado.raiz == pytest.approx(3.582575695, abs=1e-6, rel=0)
    assert abs(resultado.raiz - exacta) <= resultado.cota_error <= 1e-6
    assert abs(resultado.residuo) <= 1e-6
    assert resultado.parametros == parametros
    assert resultado.iteraciones == len(resultado.traza) <= 80
    for indice, paso in enumerate(resultado.traza):
        assert paso.iteracion == indice + 1
        assert paso.a <= exacta <= paso.b
        assert paso.c == paso.a + (paso.b - paso.a) / 2
        assert paso.semiancho == (paso.b - paso.a) / 2
        assert paso.f_c == 20 - 2 * paso.c - paso.c ** 2
        if indice:
            anterior = resultado.traza[indice - 1]
            assert paso.semiancho == anterior.semiancho / 2
            assert paso.a == anterior.c or paso.b == anterior.c
    assert resultado.traza[0].a == 0 and resultado.traza[0].b == 5


@pytest.mark.parametrize('raiz', [0, 1])
def test_raiz_exacta_en_ambos_extremos(raiz):
    resultado = biseccion(lambda x: x - raiz, 0, 1)
    assert resultado.estado == 'solucion'
    assert resultado.raiz == raiz
    assert resultado.cota_error == resultado.residuo == 0
    assert resultado.iteraciones == 0


def test_raiz_exacta_en_punto_medio_puede_parar_antes_de_la_tolerancia():
    resultado = biseccion(lambda x: x - 2, 0, 4)
    assert resultado.raiz == 2
    assert resultado.cota_error == 0
    assert resultado.iteraciones == 1
    assert resultado.traza[0].semiancho == 2


@pytest.mark.parametrize('signo', [-1, 1])
def test_mismo_signo_informa_ausencia_de_cruce_sin_inventar_raiz(signo):
    resultado = biseccion(lambda x: signo * (x + 1), 0, 2)
    assert resultado.estado == 'sin_interseccion'
    assert resultado.signo_extremos == signo
    assert resultado.raiz is resultado.residuo is resultado.cota_error is None
    assert resultado.traza == ()


def test_no_multiplica_signos_que_podrian_subdesbordarse():
    parametros = ParametrosBiseccion(tolerancia_x=1e-6)
    resultado = biseccion(lambda x: 1e-200 * (x - 0.3), 0, 1, parametros=parametros)
    assert resultado.estado == 'solucion'
    assert resultado.raiz == pytest.approx(0.3, abs=1e-6, rel=0)
    assert resultado.cota_error <= 1e-6
    assert resultado.iteraciones > 10  # Residuo pequeño por sí solo no basta.


def test_semiancho_pequeno_no_basta_si_falta_precision_en_altura():
    parametros = ParametrosBiseccion(tolerancia_x=1, tolerancia_f=1e-20, max_iteraciones=5)
    resultado = biseccion(lambda x: x * x - 2, 0, 2, parametros=parametros)
    assert resultado.estado == 'falta_convergencia'
    assert resultado.raiz is None
    assert resultado.cota_error < parametros.tolerancia_x
    assert abs(resultado.residuo) > parametros.tolerancia_f
    assert resultado.iteraciones == 5


def test_maximo_agotado_es_distinto_de_ausencia_de_cruce():
    resultado = biseccion(lambda x: x * x - 2, 0, 2,
                          parametros=ParametrosBiseccion(max_iteraciones=1))
    assert resultado.estado == 'falta_convergencia'
    assert resultado.raiz is None
    assert resultado.iteraciones == 1
    assert resultado.traza[0].a == 0 and resultado.traza[0].b == 2


@pytest.mark.parametrize('punto_invalido', [0, 0.5, 1])
def test_no_trata_valores_no_finitos_como_ausencia_de_cruce(punto_invalido):
    def funcion(x):
        return float('nan') if x == punto_invalido else x - 0.3

    with pytest.raises(ValueError, match='no finito'):
        biseccion(funcion, 0, 1)


@pytest.mark.parametrize(('a', 'b'), [(1, 1), (2, 1), (0, float('inf')), (float('nan'), 1)])
def test_intervalo_exige_amplitud_positiva_y_extremos_finitos(a, b):
    with pytest.raises(ValueError):
        biseccion(lambda x: x, a, b)


@pytest.mark.parametrize('cambios', [
    {'tolerancia_x': 0}, {'tolerancia_x': float('nan')},
    {'tolerancia_f': -1}, {'tolerancia_f': float('inf')},
    {'max_iteraciones': 0}, {'max_iteraciones': 1.5}, {'max_iteraciones': True},
])
def test_parametros_invalidos_no_ejecutan_el_solver(cambios):
    with pytest.raises(ValueError):
        ParametrosBiseccion(**cambios)
