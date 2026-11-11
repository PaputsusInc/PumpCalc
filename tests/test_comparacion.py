"""Aislamiento de escenarios, meta común y comparación con datos vigentes."""

from dataclasses import replace

import pytest

from pumpcalc.comparacion import ComparacionEscenarios
from pumpcalc.ejemplos import EJEMPLOS, escenario_ejemplo
from pumpcalc.entradas import validar_curva
from pumpcalc.presentacion import opciones_comparacion


def test_copiar_a_b_conserva_resultados_y_crea_copias_independientes():
    proyecto = ComparacionEscenarios()
    a = proyecto.sesiones['A']
    proyecto.copiar_a_b()
    b = proyecto.sesiones['B']
    assert a.entradas == b.entradas and a.entradas is not b.entradas
    assert a.puntos == b.puntos and a.puntos[0] is not b.puntos[0]
    assert a.resultado == b.resultado and a.resultado is not b.resultado
    assert a.resultado.biseccion.traza is not b.resultado.biseccion.traza
    b.editar_instalacion('diametro_mm', '32')
    b.simular()
    assert a.entradas['diametro_mm'] == '25'
    assert a.estado == 'solucion'
    assert a.resultado.punto.caudal_m3s < b.resultado.punto.caudal_m3s
    assert proyecto.evaluar_meta('A').estado == 'no_alcanza'
    assert proyecto.evaluar_meta('B').estado == 'alcanza'
    diferencia = proyecto.diferencia_caudal()
    assert diferencia.cambio_m3s * 3600 == pytest.approx(0.61630249, abs=1e-6)
    assert diferencia.diferencia_absoluta_m3s == abs(diferencia.cambio_m3s)
    assert diferencia.porcentaje > 0


def test_meta_no_recalcula_ni_invalida_los_escenarios(monkeypatch):
    proyecto = ComparacionEscenarios()
    resultados = {n: s.resultado for n, s in proyecto.sesiones.items()}
    revisiones = {n: s.revision for n, s in proyecto.sesiones.items()}
    def prohibido(*args, **kwargs):
        raise AssertionError('Cambiar la meta no debe resolver la hidráulica.')
    monkeypatch.setattr('pumpcalc.simulacion.resolver_operacion', prohibido)
    for texto in ('5', '3,5', '', '0'):
        proyecto.establecer_objetivo(texto)
        for n, sesion in proyecto.sesiones.items():
            assert sesion.resultado is resultados[n]
            assert sesion.revision == revisiones[n]
            assert sesion.estado == 'solucion'


@pytest.mark.parametrize(('texto', 'estado'), [
    ('', 'sin_meta'), ('0', 'meta_invalida'), ('NaN', 'meta_invalida'),
    ('101', 'meta_invalida'), ('3,5', 'alcanza'), ('5', 'no_alcanza'),
])
def test_evalua_meta_opcional_y_sus_errores(texto, estado):
    proyecto = ComparacionEscenarios()
    proyecto.establecer_objetivo(texto)
    assert proyecto.evaluar_meta('A').estado == estado


@pytest.mark.parametrize('factor', [-0.5, 0, 0.5])
def test_margen_dentro_de_la_cota_informa_limite_numerico(factor):
    proyecto = ComparacionEscenarios()
    resultado = proyecto.sesiones['A'].resultado
    meta = resultado.punto.caudal_m3s + factor * resultado.biseccion.cota_error
    proyecto.establecer_objetivo(str(meta * 3600))
    assert proyecto.evaluar_meta('A').estado == 'en_limite'


def test_escenario_pendiente_invalido_o_sin_cruce_no_inventa_comparacion():
    proyecto = ComparacionEscenarios()
    b = proyecto.sesiones['B']
    for valor in ('32', '0', '25'):
        b.editar_instalacion('diametro_mm', valor)
        assert proyecto.diferencia_caudal() is None
        assert proyecto.evaluar_meta('B').estado == 'sin_resultado'
    proyecto.seleccionar('B')
    proyecto.cargar_ejemplo('sin_interseccion')
    assert b.estado == 'sin_interseccion'
    assert proyecto.diferencia_caudal() is None
    assert proyecto.evaluar_meta('B').margen_m3s is None


def test_porcentaje_no_aplicable_si_q_a_es_cero():
    proyecto = ComparacionEscenarios()
    a = proyecto.sesiones['A']
    cero = replace(a.escenario, curva=validar_curva([(0, 12), (1, 12), (2, 12)]))
    a.cargar_escenario(cero)
    a.simular()
    assert a.resultado.punto.caudal_m3s == 0
    assert proyecto.diferencia_caudal().porcentaje is None
    assert proyecto.diferencia_caudal().cambio_m3s > 0


@pytest.mark.parametrize('ejemplo', list(EJEMPLOS))
def test_tres_ejemplos_se_cargan_solo_en_el_activo(ejemplo):
    proyecto = ComparacionEscenarios()
    a = proyecto.sesiones['A'].resultado
    proyecto.seleccionar('B')
    proyecto.cargar_ejemplo(ejemplo)
    assert proyecto.sesiones['A'].resultado is a
    if ejemplo == 'sin_interseccion':
        assert proyecto.sesiones['B'].estado == 'sin_interseccion'
    else:
        assert proyecto.sesiones['B'].estado == 'solucion'


def test_copiar_entradas_invalidas_o_pendientes_no_copia_un_resultado_viejo():
    proyecto = ComparacionEscenarios()
    for valor in ('0', '32'):
        proyecto.sesiones['A'].editar_instalacion('diametro_mm', valor)
        proyecto.copiar_a_b()
        b = proyecto.sesiones['B']
        assert b.resultado is None
        assert b.estado == proyecto.sesiones['A'].estado


def test_nueva_sesion_restablece_ejemplo_inicial_y_meta():
    anterior = ComparacionEscenarios()
    anterior.seleccionar('B')
    anterior.cargar_ejemplo('diametro32')
    anterior.establecer_objetivo('8')
    nueva = ComparacionEscenarios()
    assert nueva.activo == 'A'
    assert nueva.objetivo_texto == '4'
    assert all(s.entradas['diametro_mm'] == '25' for s in nueva.sesiones.values())


def test_curvas_superpuestas_conservan_dominios_y_marcadores_por_caso():
    a = escenario_ejemplo('base')
    b = replace(escenario_ejemplo('diametro32'), curva=validar_curva([(1, 34), (2, 31), (3, 26), (4, 19), (5, 10)]))
    from pumpcalc.operacion import resolver_operacion
    opciones = opciones_comparacion({'A': (a, resolver_operacion(a)), 'B': (b, resolver_operacion(b))})
    assert opciones['xAxis']['min'] == 0 and opciones['xAxis']['max'] == 5
    assert len(opciones['series']) == 8
    for serie in opciones['series']:
        minimo = 1 if serie['name'].endswith('(B)') else 0
        assert all(minimo <= q <= 5 for q, _ in serie['data'])
        if serie['name'].startswith('Sistema'):
            assert len(serie['data']) == 150


def test_comparacion_grafica_sin_cruce_omite_solo_su_marcador():
    proyecto = ComparacionEscenarios()
    proyecto.seleccionar('B')
    proyecto.cargar_ejemplo('sin_interseccion')
    opciones = opciones_comparacion({n: (s.escenario, s.resultado) for n, s in proyecto.sesiones.items()})
    marcadores = [s['name'] for s in opciones['series'] if s['name'].startswith('Punto de operación')]
    assert marcadores == ['Punto de operación (A)']
