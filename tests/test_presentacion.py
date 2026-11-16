"""Coherencia entre resultado, gráfica y tablas de explicación numérica."""

from dataclasses import replace
import math

import pytest

from pumpcalc.biseccion import ParametrosBiseccion
from pumpcalc.ejemplos import caso_base
from pumpcalc.entradas import Escenario, validar_curva
from pumpcalc.operacion import resolver_operacion
from pumpcalc.perdidas import evaluar_sistema
from pumpcalc.presentacion import filas_biseccion, filas_colebrook, opciones_curvas
from pumpcalc.simulacion import SesionSimulacion


def test_grafica_tiene_ejes_numericos_y_150_muestras_del_sistema_en_el_dominio():
    escenario = caso_base()
    resultado = resolver_operacion(escenario)
    opciones = opciones_curvas(escenario, resultado)
    assert opciones['xAxis']['type'] == opciones['yAxis']['type'] == 'value'
    assert opciones['xAxis']['name'] == 'Caudal Q (m³/h)'
    assert opciones['yAxis']['name'] == 'Altura H (m)'
    assert opciones['xAxis']['min'] == 0 and opciones['xAxis']['max'] == 5
    sistema = opciones['series'][1]['data']
    assert len(sistema) == 150
    assert sistema[0] == [0, 12]
    assert sistema[-1][0] == 5
    assert all(0 <= q <= 5 and math.isfinite(h) for q, h in sistema)
    assert all(derecho[0] > izquierdo[0] and derecho[1] > izquierdo[1]
               for izquierdo, derecho in zip(sistema, sistema[1:]))


def test_bomba_conserva_sus_segmentos_exactos_y_los_nodos_se_muestran():
    escenario = caso_base()
    opciones = opciones_curvas(escenario, resolver_operacion(escenario))
    esperados = [[0, 35], [1, 34], [2, 31], [3, 26], [4, 19], [5, 10]]
    assert opciones['series'][0]['data'] == esperados
    assert opciones['series'][0]['smooth'] is False
    assert opciones['series'][2]['type'] == 'scatter'
    assert opciones['series'][2]['data'] == esperados


def test_marcador_es_el_punto_calculado_independiente_del_muestreo():
    escenario = caso_base()
    resultado = resolver_operacion(escenario)
    esperado = [[resultado.punto.caudal_m3s * 3600, resultado.punto.altura_m]]
    assert opciones_curvas(escenario, resultado)['series'][-1]['data'] == esperado
    escasas = opciones_curvas(escenario, resultado, muestras=3)
    assert escasas['series'][-1]['name'] == 'Punto de operación'
    assert escasas['series'][-1]['data'] == esperado
    assert esperado[0][0] not in [q for q, _ in escasas['series'][1]['data']]


def test_curva_que_empieza_por_encima_de_cero_no_se_extiende_hasta_cero():
    base = caso_base()
    escenario = replace(base, curva=validar_curva([(1, 34), (2, 31), (3, 26), (4, 19), (5, 10)]))
    opciones = opciones_curvas(escenario, resolver_operacion(escenario))
    assert opciones['xAxis']['min'] == 1
    for serie in opciones['series']:
        assert all(1 <= q <= 5 for q, _ in serie['data'])


@pytest.mark.parametrize('por_debajo', [True, False])
def test_sin_interseccion_conserva_curvas_sin_marcador_inventado(por_debajo):
    escenario = caso_base()
    if por_debajo:
        escenario = replace(escenario, instalacion=replace(escenario.instalacion, desnivel_m=40))
    else:
        escenario = replace(escenario, curva=validar_curva([(0, 35), (1, 34), (2, 31)]))
    resultado = resolver_operacion(escenario)
    assert resultado.estado == 'sin_interseccion'
    opciones = opciones_curvas(escenario, resultado)
    assert len(opciones['series']) == 3
    assert len(opciones['series'][1]['data']) == 150
    assert filas_biseccion(resultado) == filas_colebrook(resultado) == []


def test_tabla_biseccion_convierte_caudales_y_cota_sin_alterar_residuos():
    resultado = resolver_operacion(caso_base())
    filas = filas_biseccion(resultado)
    assert len(filas) == resultado.biseccion.iteraciones
    assert filas[0]['a'] == 0 and filas[0]['b'] == 5
    assert filas[0]['c'] == filas[0]['cota'] == 2.5
    assert filas[0]['ea'] is None
    for fila, paso in zip(filas, resultado.biseccion.traza):
        assert fila['a'] == paso.a * 3600
        assert fila['b'] == paso.b * 3600
        assert fila['c'] == paso.c * 3600
        assert fila['cota'] == paso.semiancho * 3600
        assert fila['residuo'] == paso.f_c
    for anterior, actual in zip(filas, filas[1:]):
        assert actual['ea'] == pytest.approx(abs(actual['c'] - anterior['c']))


def test_traza_colebrook_solo_contiene_el_factor_del_resultado_final():
    resultado = resolver_operacion(caso_base())
    filas = filas_colebrook(resultado)
    colebrook = resultado.punto.sistema.friccion.colebrook
    assert len(filas) == colebrook.iteraciones
    assert filas[-1]['x'] == colebrook.traza[-1].x
    assert filas[-1]['cambio'] <= 1e-10
    assert all(fila['cambio'] == pytest.approx(abs(fila['x'] - fila['x_anterior']))
               for fila in filas)
    assert abs(filas[-1]['residuo']) <= 1e-10


@pytest.mark.parametrize('reynolds', [1000, 3000])
def test_detalle_de_laminar_y_transicion_usa_la_traza_pertinente(reynolds):
    instalacion = caso_base().instalacion
    q = reynolds * 1.004e-6 * math.pi * instalacion.diametro_m / 4
    h = evaluar_sistema(instalacion, q).altura_sistema_m
    curva = validar_curva([(0, h), (q * 3600, h), (q * 7200, h)])
    resultado = resolver_operacion(Escenario(instalacion, curva))
    assert resultado.estado == 'solucion'
    if reynolds == 1000:
        assert resultado.punto.sistema.friccion.regimen == 'laminar'
        assert filas_colebrook(resultado) == []
    else:
        assert resultado.punto.sistema.friccion.regimen == 'transicion'
        assert resultado.punto.sistema.friccion.colebrook.reynolds == 4000
        assert filas_colebrook(resultado)


def test_raiz_cero_se_marca_como_solucion_y_no_tiene_traza_de_friccion():
    escenario = caso_base()
    escenario = replace(escenario, curva=validar_curva([(0, 12), (1, 12), (2, 12)]))
    resultado = resolver_operacion(escenario)
    opciones = opciones_curvas(escenario, resultado)
    assert opciones['series'][-1]['data'] == [[0, 12]]
    assert filas_colebrook(resultado) == filas_biseccion(resultado) == []


def test_falta_de_convergencia_conserva_su_traza_sin_marcador():
    escenario = caso_base()
    resultado = resolver_operacion(escenario, parametros=ParametrosBiseccion(max_iteraciones=1))
    assert len(filas_biseccion(resultado)) == 1
    assert filas_colebrook(resultado) == []
    assert len(opciones_curvas(escenario, resultado)['series']) == 3


def test_editar_invalida_el_resultado_que_alimentaba_grafica_y_tablas():
    sesion = SesionSimulacion()
    sesion.simular()
    antes = opciones_curvas(sesion.escenario, sesion.resultado)
    sesion.editar_instalacion('diametro_mm', '32')
    assert sesion.resultado is None
    sesion.simular()
    despues = opciones_curvas(sesion.escenario, sesion.resultado)
    assert antes['series'][-1]['data'] != despues['series'][-1]['data']


@pytest.mark.parametrize('muestras', [1, 0, 1.5, True])
def test_muestreo_exige_cantidad_entera_suficiente(muestras):
    escenario = caso_base()
    with pytest.raises(ValueError):
        opciones_curvas(escenario, resolver_operacion(escenario), muestras=muestras)
