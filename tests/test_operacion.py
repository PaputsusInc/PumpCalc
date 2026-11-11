"""Casos completos y estados del punto de operación de la línea base."""

from dataclasses import replace

import pytest

from pumpcalc.biseccion import ParametrosBiseccion
from pumpcalc.ejemplos import caso_base
from pumpcalc.entradas import Escenario, validar_curva
from pumpcalc.operacion import resolver_operacion
from pumpcalc.perdidas import evaluar_sistema


@pytest.mark.parametrize(('cambios', 'q_referencia', 'h_referencia'), [
    ({}, 3.765443, 20.641896),
    ({'diametro_m': 0.032}, 4.381758, 15.564175),
    ({'longitud_m': 80}, 3.227947, 24.404369),
])
def test_referencias_hidraulicas_completas(cambios, q_referencia, h_referencia):
    base = caso_base()
    escenario = replace(base, instalacion=replace(base.instalacion, **cambios))
    resultado = resolver_operacion(escenario)
    assert resultado.estado == 'solucion'
    assert resultado.metodo_fallido is None
    punto = resultado.punto
    assert punto.caudal_m3s * 3600 == pytest.approx(q_referencia, abs=0.001, rel=0)
    assert punto.altura_m == pytest.approx(h_referencia, abs=0.001, rel=0)
    assert abs(punto.altura_m - punto.sistema.altura_sistema_m) <= 1e-4
    assert abs(resultado.biseccion.residuo) <= 1e-4
    assert resultado.biseccion.cota_error <= 1e-7
    assert punto.tramo[0].caudal_m3s <= punto.caudal_m3s <= punto.tramo[1].caudal_m3s
    assert punto.sistema.friccion.regimen == 'turbulento'
    assert punto.sistema.friccion.colebrook.reynolds == punto.sistema.reynolds
    assert resultado.biseccion.traza[0].a == 0
    assert resultado.biseccion.traza[0].b == 5 / 3600
    if not cambios:
        assert punto.sistema.friccion.factor_darcy == pytest.approx(0.020839985, abs=1e-7, rel=0)


def test_diametro_mayor_aumenta_q_y_reduce_velocidad():
    a = caso_base()
    b = replace(a, instalacion=replace(a.instalacion, diametro_m=0.032))
    resultado_a, resultado_b = resolver_operacion(a), resolver_operacion(b)
    assert resultado_b.punto.caudal_m3s > resultado_a.punto.caudal_m3s
    assert resultado_b.punto.sistema.velocidad_ms < resultado_a.punto.sistema.velocidad_ms
    assert resultado_b.punto.sistema.velocidad_ms == pytest.approx(1.513408, abs=1e-4, rel=0)
    assert a.instalacion.diametro_m == 0.025


def test_desnivel_40_no_tiene_cruce_ni_caudal_inventado():
    base = caso_base()
    escenario = replace(base, instalacion=replace(base.instalacion, desnivel_m=40))
    resultado = resolver_operacion(escenario)
    assert resultado.estado == 'sin_interseccion'
    assert resultado.punto is None
    assert resultado.biseccion.raiz is None
    assert resultado.biseccion.signo_extremos == -1
    assert 'por debajo' in resultado.mensaje
    assert 'intervalo disponible' in resultado.mensaje


def test_curva_por_encima_del_sistema_en_el_intervalo_ingresado():
    base = caso_base()
    escenario = replace(base, curva=validar_curva([(0, 35), (1, 34), (2, 31)]))
    resultado = resolver_operacion(escenario)
    assert resultado.estado == 'sin_interseccion'
    assert resultado.punto is None
    assert resultado.biseccion.signo_extremos == 1
    assert 'por encima' in resultado.mensaje
    assert 'intervalo disponible' in resultado.mensaje


def test_curva_puede_empezar_por_encima_de_caudal_cero():
    base = caso_base()
    escenario = replace(base, curva=validar_curva([(1, 34), (2, 31), (3, 26), (4, 19), (5, 10)]))
    resultado = resolver_operacion(escenario)
    assert resultado.estado == 'solucion'
    assert resultado.punto.caudal_m3s * 3600 == pytest.approx(3.765443, abs=0.001, rel=0)
    assert resultado.biseccion.traza[0].a == 1 / 3600


@pytest.mark.parametrize('q_m3h', [1, 2, 3])
def test_raiz_en_extremos_y_nodo_interior(q_m3h):
    # Curva fabricada para probar el solver en una igualdad exacta conocida;
    # las referencias numéricas independientes se verifican en otra prueba.
    instalacion = caso_base().instalacion
    altura = evaluar_sistema(instalacion, q_m3h / 3600).altura_sistema_m
    curva = validar_curva([(1, altura), (2, altura), (3, altura)])
    resultado = resolver_operacion(Escenario(instalacion, curva))
    assert resultado.estado == 'solucion'
    assert abs(resultado.punto.caudal_m3s - q_m3h / 3600) <= resultado.biseccion.cota_error
    assert resultado.biseccion.cota_error <= 1e-7
    assert abs(resultado.biseccion.residuo) <= 1e-4
    if q_m3h != 2:
        assert resultado.biseccion.cota_error == 0
        assert resultado.biseccion.iteraciones == 0
    # En el nodo interior, el punto medio puede diferir un ulp del Q tabulado.


def test_cruce_en_nodo_exacto_muestra_el_tramo_que_termina_en_el_nodo():
    instalacion = caso_base().instalacion
    caudal = 2 / 3600
    altura = evaluar_sistema(instalacion, caudal).altura_sistema_m
    curva = validar_curva([(0, altura), (2, altura), (4, altura)])

    resultado = resolver_operacion(Escenario(instalacion, curva))

    assert resultado.punto.caudal_m3s == caudal
    assert resultado.punto.altura_m == altura
    assert resultado.punto.tramo == curva.puntos[:2]


def test_raiz_cero_es_solucion_valida_distinta_de_falta_de_cruce():
    base = caso_base()
    escenario = replace(base, curva=validar_curva([(0, 12), (1, 12), (2, 12)]))
    resultado = resolver_operacion(escenario, max_iteraciones_colebrook=1)
    assert resultado.estado == 'solucion'
    assert resultado.punto.caudal_m3s == 0
    assert resultado.punto.sistema.velocidad_ms == 0
    assert resultado.punto.sistema.friccion.factor_darcy is None
    assert resultado.punto.altura_m == 12


def test_biseccion_sin_convergencia_no_se_presenta_como_sin_interseccion():
    resultado = resolver_operacion(caso_base(), parametros=ParametrosBiseccion(max_iteraciones=1))
    assert resultado.estado == 'falta_convergencia'
    assert resultado.metodo_fallido == 'biseccion'
    assert resultado.punto is None
    assert resultado.biseccion.iteraciones == 1


def test_fallo_de_colebrook_no_produce_una_solucion_aparente():
    resultado = resolver_operacion(caso_base(), max_iteraciones_colebrook=1)
    assert resultado.estado == 'falta_convergencia'
    assert resultado.metodo_fallido == 'colebrook'
    assert resultado.punto is None
    assert resultado.biseccion is None
    assert 'Colebrook' in resultado.mensaje


def test_curva_incompleta_por_debajo_no_permite_concluir_fuera_del_dominio():
    base = caso_base()
    escenario = replace(base, curva=validar_curva([(1, 10), (2, 9), (3, 8)]))
    resultado = resolver_operacion(escenario)
    assert resultado.estado == 'sin_interseccion'
    assert resultado.punto is None
    assert 'por debajo' in resultado.mensaje
    assert 'intervalo disponible' in resultado.mensaje
