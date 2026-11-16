"""RK4 y conservación de agua en el llenado 3D."""

import math

import pytest

from pumpcalc.ejemplos import caso_base
from pumpcalc.entradas import ErrorEntrada
from pumpcalc.transitorio import paso_runge_kutta4, simular_llenado, validar_tanques


DATOS = {
    'origen_area_m2': '1', 'origen_capacidad_m3': '1,6', 'origen_inicial_m3': '1,2',
    'destino_area_m2': '1', 'destino_capacidad_m3': '1,6', 'destino_inicial_m3': '0,2',
}


def test_paso_rk4_reproduce_una_solucion_conocida():
    # y' = y, y(0) = 1 => y(0,1) = e^0,1.
    aproximacion = 1 + paso_runge_kutta4(lambda y: y, 1, .1)
    assert aproximacion == pytest.approx(math.exp(.1), abs=1e-7)


def test_llenado_recalcula_caudal_y_conserva_volumen():
    tanques = validar_tanques(DATOS)
    trayectoria = simular_llenado(caso_base(), tanques)
    estados = trayectoria.estados
    assert trayectoria.motivo_parada == 'Origen vacío o destino lleno'
    assert estados[0].caudal_m3s * 3600 == pytest.approx(3.765449524, abs=1e-6)
    assert estados[-1].origen_m3 == 0
    assert estados[-1].destino_m3 == pytest.approx(1.4)
    assert all(e.origen_m3 + e.destino_m3 == pytest.approx(1.4) for e in estados)
    assert all(a.origen_m3 >= b.origen_m3 and a.destino_m3 <= b.destino_m3
               for a, b in zip(estados, estados[1:]))
    assert estados[len(estados) // 2].caudal_m3s < estados[0].caudal_m3s
    refinada = simular_llenado(caso_base(), tanques, paso_s=5)
    assert abs(estados[-1].tiempo_s - refinada.estados[-1].tiempo_s) < .01


def test_volumen_inicial_y_capacidad_controlan_la_parada():
    datos = DATOS | {'destino_inicial_m3': '1.5'}
    trayectoria = simular_llenado(caso_base(), validar_tanques(datos))
    assert trayectoria.estados[-1].destino_m3 == pytest.approx(1.6)
    assert trayectoria.estados[-1].origen_m3 == pytest.approx(1.1)
    sin_agua = DATOS | {'origen_inicial_m3': '0'}
    assert len(simular_llenado(caso_base(), validar_tanques(sin_agua)).estados) == 1


def test_entrada_de_tanque_invalida_identifica_el_campo():
    with pytest.raises(ErrorEntrada) as error:
        validar_tanques(DATOS | {'destino_inicial_m3': '2'})
    assert error.value.campo == 'destino_inicial_m3'
