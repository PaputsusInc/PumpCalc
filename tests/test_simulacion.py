"""Coherencia entre ediciones, validación, recálculo y resultados vigentes."""

from pumpcalc.biseccion import ParametrosBiseccion
from pumpcalc.operacion import resolver_operacion
from pumpcalc.simulacion import SesionSimulacion


def sesion_calculada():
    sesion = SesionSimulacion()
    sesion.simular()
    return sesion


def test_inicio_calcula_el_caso_base_y_editar_retira_el_resultado():
    sesion = sesion_calculada()
    assert sesion.estado == 'solucion'
    assert abs(sesion.resultado.punto.caudal_m3s * 3600 - 3.765443) < 0.001
    sesion.editar_instalacion('diametro_mm', '32')
    assert sesion.estado == 'pendiente'
    assert sesion.resultado is None
    assert sesion.simular_revision(sesion.revision)
    assert sesion.estado == 'solucion'
    assert abs(sesion.resultado.punto.caudal_m3s * 3600 - 4.381758) < 0.001


def test_revision_antigua_no_publica_resultados_de_datos_anteriores():
    sesion = sesion_calculada()
    sesion.editar_instalacion('diametro_mm', '32')
    revision_antigua = sesion.revision
    sesion.editar_instalacion('diametro_mm', '40')
    assert not sesion.simular_revision(revision_antigua)
    assert sesion.resultado is None
    assert sesion.estado == 'pendiente'
    assert sesion.simular_revision(sesion.revision)
    assert sesion.resultado.punto.sistema.caudal_m3s == sesion.resultado.punto.caudal_m3s


def test_entrada_invalida_elimina_resultado_y_conserva_el_resto_del_formulario():
    sesion = sesion_calculada()
    sesion.editar_instalacion('diametro_mm', '')
    assert sesion.estado == 'datos_invalidos'
    assert sesion.error.campo == 'diametro_mm'
    assert sesion.resultado is None and sesion.escenario is None
    assert sesion.entradas['longitud_m'] == '40'
    assert not sesion.simular_revision(sesion.revision)
    sesion.simular()
    assert sesion.estado == 'datos_invalidos'
    sesion.editar_instalacion('diametro_mm', '25,0')
    sesion.simular()
    assert sesion.estado == 'solucion'
    assert sesion.error is None


def test_editar_la_curva_valida_cada_celda_y_no_conserva_resultados():
    sesion = sesion_calculada()
    sesion.editar_punto(1, 0, '0')
    assert sesion.estado == 'datos_invalidos'
    assert sesion.error.campo == 'puntos.2.caudal_m3h'
    assert sesion.resultado is None
    sesion.editar_punto(1, 0, '1')
    sesion.editar_punto(1, 1, '33')
    assert sesion.estado == 'pendiente'
    sesion.simular()
    assert sesion.estado == 'solucion'
    assert sesion.escenario.curva.puntos[1].altura_m == 33


def test_agregar_y_quitar_puntos_respeta_3_a_10_e_invalida():
    sesion = sesion_calculada()
    assert sesion.agregar_punto()
    assert sesion.resultado is None
    assert sesion.estado == 'datos_invalidos'
    assert sesion.error.campo == 'puntos.7.caudal_m3h'
    assert sesion.quitar_punto(6)
    assert sesion.estado == 'pendiente'
    while len(sesion.puntos) > 3:
        assert sesion.quitar_punto(len(sesion.puntos) - 1)
    assert not sesion.quitar_punto(0)
    while len(sesion.puntos) < 10:
        assert sesion.agregar_punto()
    assert not sesion.agregar_punto()


def test_cargar_base_restaura_entradas_y_simular_cancela_revisiones_pendientes():
    sesion = sesion_calculada()
    sesion.editar_instalacion('diametro_mm', '32')
    revision = sesion.revision
    sesion.simular()
    assert not sesion.simular_revision(revision)
    sesion.cargar_base()
    sesion.simular()
    assert sesion.entradas['diametro_mm'] == '25'
    assert len(sesion.puntos) == 6
    assert abs(sesion.resultado.punto.caudal_m3s * 3600 - 3.765443) < 0.001


def test_ausencia_de_interseccion_no_presenta_un_caudal():
    sesion = sesion_calculada()
    sesion.editar_instalacion('desnivel_m', '40')
    sesion.simular()
    assert sesion.estado == 'sin_interseccion'
    assert sesion.resultado.punto is None
    assert 'por debajo' in sesion.resultado.mensaje


def test_falta_de_convergencia_conserva_su_estado(monkeypatch):
    monkeypatch.setattr(
        'pumpcalc.simulacion.resolver_operacion',
        lambda escenario: resolver_operacion(escenario, parametros=ParametrosBiseccion(max_iteraciones=1)),
    )
    sesion = sesion_calculada()
    assert sesion.estado == 'falta_convergencia'
    assert sesion.resultado.punto is None


def test_dos_sesiones_no_comparten_entradas_curva_ni_resultado():
    a, b = sesion_calculada(), sesion_calculada()
    b.editar_instalacion('diametro_mm', '32')
    b.editar_punto(0, 1, '40')
    assert a.entradas['diametro_mm'] == '25'
    assert a.puntos[0][1] == '35'
    assert a.estado == 'solucion'


def test_datos_generales_se_validan_sin_modificar_el_calculo_y_se_copian():
    sesion = sesion_calculada()
    revision = sesion.revision
    resultado = sesion.resultado
    sesion.editar_dato_bomba('potencia_hp', '1,5')
    sesion.editar_dato_bomba('altura_maxima_m', '35')
    sesion.editar_dato_bomba('caudal_maximo_m3h', '6')
    assert sesion.errores_datos_bomba == {}
    assert sesion.revision == revision
    assert sesion.resultado is resultado
    copia = sesion.copiar()
    assert copia.datos_bomba == sesion.datos_bomba
    copia.editar_dato_bomba('potencia_hp', '2')
    assert sesion.datos_bomba['potencia_hp'] == '1,5'

    sesion.editar_dato_bomba('altura_maxima_m', '34')
    sesion.editar_dato_bomba('caudal_maximo_m3h', '4')
    sesion.editar_dato_bomba('potencia_hp', 'abc')
    assert set(sesion.errores_datos_bomba) == {
        'altura_maxima_m', 'caudal_maximo_m3h', 'potencia_hp',
    }
    assert sesion.resultado is resultado
    sesion.cargar_base()
    assert all(not valor for valor in sesion.datos_bomba.values())
