"""Escala visual, avance temporal y geometría sin depender del navegador."""

import base64
from dataclasses import replace
import xml.etree.ElementTree as ET

import pytest

from pumpcalc.animacion import (
    LONGITUD_RECORRIDO, NUMERO_TRAZAS, MovimientoFlujo, capa_trazas,
    fondo_instalacion, fuente_svg, grosor_tuberia, posicion_traza, rapidez_visual,
)
from pumpcalc.ejemplos import caso_base
from pumpcalc.entradas import validar_curva
from pumpcalc.operacion import resolver_operacion


def test_escala_comun_es_cero_en_reposo_y_creciente_hasta_240():
    velocidades = [0, 0.1, 1, 2, 5, 100]
    rapideces = [rapidez_visual(v) for v in velocidades]
    assert rapideces[0] == 0
    assert rapidez_visual(2) == 120
    assert all(0 <= rapidez < 240 for rapidez in rapideces)
    assert rapideces == sorted(set(rapideces))


@pytest.mark.parametrize('velocidad', [-1, float('nan'), float('inf')])
def test_rechaza_velocidades_invalidas(velocidad):
    with pytest.raises(ValueError):
        rapidez_visual(velocidad)


def test_mayor_diametro_aumenta_grosor_y_caudal_pero_reduce_rapidez():
    a = caso_base()
    b = replace(a, instalacion=replace(a.instalacion, diametro_m=0.032))
    ra, rb = resolver_operacion(a), resolver_operacion(b)
    ma, mb = MovimientoFlujo(), MovimientoFlujo()
    ma.sincronizar('solucion', ra)
    mb.sincronizar('solucion', rb)
    assert rb.punto.caudal_m3s > ra.punto.caudal_m3s
    assert mb.velocidad_ms < ma.velocidad_ms
    assert mb.rapidez_px_s < ma.rapidez_px_s
    assert grosor_tuberia(0.032) > grosor_tuberia(0.025)
    assert grosor_tuberia(0.01) < grosor_tuberia(0.025) < grosor_tuberia(0.2)


def test_avance_depende_del_tiempo_y_no_del_numero_de_fotogramas():
    resultado = resolver_operacion(caso_base())
    uno, varios = MovimientoFlujo(), MovimientoFlujo()
    uno.sincronizar('solucion', resultado)
    varios.sincronizar('solucion', resultado)
    uno.avanzar(1)
    for _ in range(10):
        varios.avanzar(0.1)
    assert uno.fase_px == pytest.approx(varios.fase_px)
    assert uno.fase_px == pytest.approx(rapidez_visual(resultado.punto.sistema.velocidad_ms))
    assert 0 <= uno.fase_px < LONGITUD_RECORRIDO


def test_pausa_y_reanudacion_conservan_fase_y_resultado_hidraulico():
    resultado = resolver_operacion(caso_base())
    movimiento = MovimientoFlujo()
    movimiento.sincronizar('solucion', resultado)
    movimiento.avanzar(0.1)
    antes = movimiento.fase_px
    movimiento.pausada = True
    assert not movimiento.avanzar(10)
    assert movimiento.fase_px == antes
    movimiento.pausada = False
    assert movimiento.avanzar(0.1)
    assert movimiento.fase_px > antes
    assert resultado.punto.caudal_m3s * 3600 == pytest.approx(3.765449524)


@pytest.mark.parametrize('estado', ['pendiente', 'datos_invalidos', 'sin_interseccion', 'falta_convergencia'])
def test_estados_sin_solucion_vigente_suspende_movimiento(estado):
    resultado = resolver_operacion(caso_base())
    movimiento = MovimientoFlujo()
    movimiento.sincronizar('solucion', resultado)
    movimiento.avanzar(0.1)
    fase = movimiento.fase_px
    movimiento.sincronizar(estado, resultado)
    assert movimiento.velocidad_ms is None
    assert not movimiento.avanzar(1)
    assert movimiento.fase_px == fase


def test_solucion_cero_permanece_distinta_de_ausencia_de_solucion():
    base = caso_base()
    cero = replace(base, curva=validar_curva([(0, 12), (1, 12), (2, 12)]))
    resultado = resolver_operacion(cero)
    movimiento = MovimientoFlujo()
    movimiento.sincronizar('solucion', resultado)
    assert movimiento.velocidad_ms == 0
    assert not movimiento.avanzar(1)
    movimiento.sincronizar('sin_interseccion', None)
    assert movimiento.velocidad_ms is None


@pytest.mark.parametrize(('distancia', 'posicion'), [
    (0, (150, 265)), (405, (555, 265)), (525, (555, 145)),
    (655, (685, 145)), (665, (150, 265)),
])
def test_trazas_siguen_la_tuberia_del_origen_al_destino(distancia, posicion):
    assert posicion_traza(distancia) == posicion


def test_capa_movil_solo_contiene_trazas_y_cambia_con_la_fase():
    capa = capa_trazas(0, 24)
    raiz = ET.fromstring(capa)
    assert len(raiz.findall('circle')) == NUMERO_TRAZAS
    assert raiz.findall('text') == raiz.findall('path') == []
    assert capa != capa_trazas(10, 24)


def test_fondo_contiene_etiquetas_resultado_y_niveles_fijos():
    escenario = caso_base()
    resultado = resolver_operacion(escenario)
    svg = fondo_instalacion(escenario.instalacion, resultado)
    raiz = ET.fromstring(svg)
    assert raiz.attrib['viewBox'] == '0 0 840 380'
    assert 'Q = 3,765450 m³/h' in svg
    assert 'D = 25,00 mm' in svg and 'L = 40,00 m' in svg and 'Δz = 12,00 m' in svg
    sin_solucion = fondo_instalacion(escenario.instalacion, None)
    assert 'Q = — m³/h' in sin_solucion
    assert 'v = — m/s' in sin_solucion
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    aguas = [r.attrib for r in raiz.findall('svg:g/svg:rect', ns)]
    aguas_sin_solucion = [r.attrib for r in ET.fromstring(sin_solucion).findall('svg:g/svg:rect', ns)]
    assert aguas == aguas_sin_solucion
    assert base64.b64decode(fuente_svg(svg).split(',', 1)[1]).decode('utf-8') == svg


@pytest.mark.parametrize('segundos', [-1, float('nan'), float('inf')])
def test_intervalo_temporal_debe_ser_finito_no_negativo(segundos):
    with pytest.raises(ValueError):
        MovimientoFlujo().avanzar(segundos)
