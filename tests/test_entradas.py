"""Dominios y conversiones de la sección 5 de la línea base vigente."""

from dataclasses import FrozenInstanceError

import pytest

from pumpcalc.ejemplos import caso_base, objetivo_demostracion_m3s
from pumpcalc.entradas import (
    CurvaBomba, ErrorEntrada, Instalacion, PuntoBomba, numero_decimal,
    validar_curva, validar_instalacion, validar_objetivo,
)


def instalacion(**cambios):
    datos = dict(longitud_m='40', diametro_mm='25', desnivel_m='12',
                 rugosidad_mm='0,0015', k_total='4')
    datos.update(cambios)
    return validar_instalacion(**datos)


@pytest.mark.parametrize(('entrada', 'esperado'), [
    (' 2,5 ', 2.5), ('2.5', 2.5), (0, 0), ('0', 0),
    ('0,0', 0), (1.25, 1.25), ('1e-3', 0.001), ('.5', 0.5),
])
def test_decimal_con_coma_o_punto(entrada, esperado):
    assert numero_decimal(entrada, 'dato') == esperado


@pytest.mark.parametrize('entrada', [
    None, '', '  ', True, [], {}, 'abc', '1 000', '1_000', '1,000.5',
    '1.000,5', '1,2,3', 'NaN', 'Infinity', float('nan'),
    float('inf'), -float('inf'), '1e309',
])
def test_formato_invalido_o_no_finito_identifica_el_campo(entrada):
    with pytest.raises(ErrorEntrada) as error:
        numero_decimal(entrada, 'dato')
    assert error.value.campo == 'dato'


def test_conversiones_del_caso_base_son_si_y_no_datos_del_motor_antiguo():
    base = caso_base()
    assert base.instalacion.longitud_m == 40
    assert base.instalacion.diametro_m == 0.025
    assert base.instalacion.desnivel_m == 12
    assert base.instalacion.rugosidad_m == pytest.approx(0.0000015)
    assert base.instalacion.k_total == 4
    assert base.curva.puntos[1].caudal_m3s == pytest.approx(1 / 3600)
    assert base.curva.puntos[-1].caudal_m3s == pytest.approx(5 / 3600)
    assert objetivo_demostracion_m3s() == pytest.approx(4 / 3600)


@pytest.mark.parametrize(('campo', 'valor'), [
    ('longitud_m', 0), ('longitud_m', -1), ('longitud_m', 1000.01),
    ('longitud_m', 11.99), ('longitud_m', ''),
    ('diametro_mm', 0), ('diametro_mm', 9.99), ('diametro_mm', 200.01),
    ('desnivel_m', -0.01), ('desnivel_m', 100.01),
    ('rugosidad_mm', -0.01), ('rugosidad_mm', 1.01),
    ('k_total', -0.01), ('k_total', 100.01),
])
def test_rechaza_limites_invalidos(campo, valor):
    with pytest.raises(ErrorEntrada) as error:
        instalacion(**{campo: valor})
    assert error.value.campo == campo


@pytest.mark.parametrize('campo', [
    'longitud_m', 'diametro_mm', 'desnivel_m', 'rugosidad_mm', 'k_total',
])
@pytest.mark.parametrize('valor', ['nan', float('inf'), None])
def test_todos_los_campos_de_instalacion_son_obligatorios_y_finitos(campo, valor):
    with pytest.raises(ErrorEntrada) as error:
        instalacion(**{campo: valor})
    assert error.value.campo == campo


@pytest.mark.parametrize('cambios', [
    dict(longitud_m=0.01, desnivel_m=0, diametro_mm=10, rugosidad_mm=0, k_total=0),
    dict(longitud_m=1000, desnivel_m=100, diametro_mm=200, rugosidad_mm=1, k_total=100),
    dict(longitud_m=12),
    dict(diametro_mm=20, rugosidad_mm=1),  # ε/D = 0,05, frontera incluida
])
def test_acepta_fronteras_y_longitud_igual_al_desnivel(cambios):
    instalacion(**cambios)


def test_limite_de_rugosidad_relativa_se_aplica_ademas_del_absoluto():
    with pytest.raises(ErrorEntrada) as error:
        instalacion(diametro_mm=10, rugosidad_mm=0.5001)
    assert error.value.campo == 'rugosidad_mm'


@pytest.mark.parametrize('entrada', [None, '', '  '])
def test_objetivo_opcional_vacio_es_ausencia(entrada):
    assert validar_objetivo(entrada) is None


@pytest.mark.parametrize('entrada', [0, '0', -1, 100.01, 'nan', float('inf')])
def test_objetivo_presente_debe_ser_positivo_y_hasta_100(entrada):
    with pytest.raises(ErrorEntrada) as error:
        validar_objetivo(entrada)
    assert error.value.campo == 'objetivo_m3h'


@pytest.mark.parametrize(('entrada', 'esperado'), [('4,5', 4.5 / 3600), (100, 100 / 3600)])
def test_objetivo_se_convierte_a_m3s(entrada, esperado):
    assert validar_objetivo(entrada) == pytest.approx(esperado)


@pytest.mark.parametrize('cantidad', [0, 1, 2, 11])
def test_curva_exige_de_3_a_10_puntos(cantidad):
    with pytest.raises(ErrorEntrada) as error:
        validar_curva([(q, 100 - q) for q in range(cantidad)])
    assert error.value.campo == 'puntos'


@pytest.mark.parametrize('cantidad', [3, 10])
def test_curva_acepta_ambas_fronteras_de_cantidad(cantidad):
    curva = validar_curva([(q, 100 - q) for q in range(cantidad)])
    assert len(curva.puntos) == cantidad


@pytest.mark.parametrize('puntos', [
    [(0, 35), (1, 34), (1, 33)],  # duplicados
    [(0, 35), (2, 34), (1, 33)],  # desorden
    [(0, 35), (1, 34), (2, 36)],  # altura creciente
    [(0, 35), (0, 34), (0, 33)],  # dominio sin amplitud
])
def test_curva_rechaza_sin_reordenar_o_modificar_las_filas(puntos):
    original = puntos.copy()
    with pytest.raises(ErrorEntrada):
        validar_curva(puntos)
    assert puntos == original


@pytest.mark.parametrize(('fila', 'campo'), [
    ((-1, 35), 'caudal_m3h'), ((100.01, 35), 'caudal_m3h'),
    (('', 35), 'caudal_m3h'), ((float('inf'), 35), 'caudal_m3h'),
    ((0, -0.01), 'altura_m'), ((0, 200.01), 'altura_m'),
    ((0, ''), 'altura_m'), ((0, float('nan')), 'altura_m'),
])
def test_campos_de_curva_identifican_fila_y_columna(fila, campo):
    with pytest.raises(ErrorEntrada) as error:
        validar_curva([fila, (1, 34), (2, 31)])
    assert error.value.campo == f'puntos.1.{campo}'


@pytest.mark.parametrize('fila', [(), (0,), (0, 35, 1), None, '0;35'])
def test_fila_de_curva_exige_exactamente_dos_valores(fila):
    with pytest.raises(ErrorEntrada) as error:
        validar_curva([fila, (1, 34), (2, 31)])
    assert error.value.campo == 'puntos.1'


def test_curva_acepta_caudal_inicial_positivo_alturas_iguales_y_limites():
    curva = validar_curva([('1,5', '200'), ('2', '200'), ('100', '0')])
    assert curva.dominio_m3s == (1.5 / 3600, 100 / 3600)
    assert curva.puntos[0].altura_m == curva.puntos[1].altura_m == 200


def test_objetos_si_no_permiten_saltar_los_limites_numericos():
    with pytest.raises(ErrorEntrada):
        Instalacion(40, 0, 12, 0, 4)
    with pytest.raises(ErrorEntrada):
        PuntoBomba(float('nan'), 35)
    with pytest.raises(ErrorEntrada):
        CurvaBomba((PuntoBomba(0, 35), PuntoBomba(0, 34), PuntoBomba(1 / 3600, 31)))


def test_ejemplos_y_curvas_no_comparten_listas_mutables():
    a, b = caso_base(), caso_base()
    assert a == b
    assert a is not b
    assert a.instalacion is not b.instalacion
    assert a.curva is not b.curva
    with pytest.raises(FrozenInstanceError):
        b.instalacion.diametro_m = 0.032
    puntos = list(a.curva.puntos)
    curva = CurvaBomba(puntos)
    puntos.clear()
    assert len(curva.puntos) == 6
