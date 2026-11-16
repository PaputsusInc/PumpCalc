"""Estado 3D coherente con el resultado, además del cambio de vista."""

import asyncio
from dataclasses import replace
from pathlib import Path

import pytest
from nicegui import ui
from nicegui.testing.user_simulation import user_simulation

from pumpcalc.escena3d import (ALTURA_TOMA, ANCHO_AGUA_DESTINO, ANCHO_AGUA_ORIGEN, FONDO_AGUA,
                               AguaEnTuberia, CanalAgua,
                               SuperficieAgua, TanqueLlenado, geometria_3d,
                               rapidez_3d)
from pumpcalc.ejemplos import caso_base


APP = Path(__file__).resolve().parents[1] / 'app.py'


def test_geometria_conserva_orden_de_las_entradas_y_flujo_no_inventa_velocidad():
    base = caso_base().instalacion
    g = geometria_3d(base)
    assert g.nivel_destino > g.nivel_origen
    assert g.nivel_inicial_destino == g.nivel_destino
    assert g.nivel_origen - g.descenso_origen == pytest.approx(g.nivel_final_origen)
    assert g.nivel_final_origen == ALTURA_TOMA
    assert g.maximo_origen > g.nivel_origen
    assert g.maximo_destino > g.nivel_destino
    assert geometria_3d(replace(base, desnivel_m=0)).nivel_destino == g.nivel_origen
    assert geometria_3d(replace(base, desnivel_m=30)).nivel_destino > g.nivel_destino
    assert geometria_3d(replace(base, longitud_m=80)).x_destino > g.x_destino
    assert geometria_3d(replace(base, diametro_m=.032)).radio > g.radio
    assert rapidez_3d(0) == 0
    assert 0 < rapidez_3d(1) < rapidez_3d(2)
    with pytest.raises(ValueError):
        rapidez_3d(-1)


def test_vista_3d_sigue_solucion_pausa_error_y_cambio_a_2d(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            (scene,) = user.find(ui.scene).elements
            (flujo,) = [obj for obj in scene.objects.values() if isinstance(obj, AguaEnTuberia)]
            superficies = [obj for obj in scene.objects.values() if isinstance(obj, SuperficieAgua)]
            (llenado,) = [obj for obj in scene.objects.values() if isinstance(obj, TanqueLlenado)]
            canales = [obj for obj in scene.objects.values() if isinstance(obj, CanalAgua)]
            assert len(superficies) == 1
            assert len(canales) == 2 and all(c.activa for c in canales)
            assert flujo.activa and flujo.rapidez > 0 and not flujo.pausada
            assert llenado.activa and llenado.trayectoria[0][3] == pytest.approx(flujo.rapidez)
            assert llenado.trayectoria[0][5:7] == pytest.approx([1.2, 0.2])
            assert llenado.trayectoria[-1][5] < 1.2
            assert llenado.trayectoria[-1][6] > 0.2
            assert superficies[0].args[4] == pytest.approx(geometria_3d(caso_base().instalacion).descenso_origen)
            assert llenado.args[3] < llenado.args[4]
            assert any(type(obj).__name__ == 'Gltf' for obj in scene.objects.values())
            await user.should_see('Q  3.765 m³/h')
            assert any(obj.args[0] == 'DEPÓSITO DE DESCARGA' for obj in scene.objects.values()
                       if type(obj).__name__ == 'Text')
            user.find('Pausar animación').click()
            assert flujo.pausada and llenado.pausada and all(s.pausada for s in superficies + canales)
            user.find('Reanudar animación').click()
            assert not flujo.pausada
            user.find(marker='reproducir-A').click()
            assert not flujo.pausada and not llenado.pausada
            (diametro,) = user.find(kind=ui.input, content='Diámetro interno D (mm)').elements
            with user:
                diametro.set_value('0')
            await user.should_see('Datos inválidos')
            assert not flujo.activa
            assert not llenado.activa
            assert not any(c.activa for c in canales)
            await user.should_see('Q  — m³/h')
            user.find('Cargar caso base').click()
            await user.should_see('Q  3.765 m³/h')
            (desnivel,) = user.find(kind=ui.input, content='Desnivel Δz (m)').elements
            with user:
                desnivel.set_value('40')
            await user.should_see('Sin punto de operación en el intervalo ingresado', retries=10)
            (flujo,) = [obj for obj in scene.objects.values() if isinstance(obj, AguaEnTuberia)]
            assert not flujo.activa
            (selector,) = user.find(marker='selector-vista').elements
            with user:
                selector.set_value('2D')
            assert len(user.find(ui.interactive_image).elements) == 1
            with user:
                selector.set_value('3D')
            assert len(user.find(ui.scene).elements) == 1

    asyncio.run(recorrido())
    assert not [registro for registro in caplog.records if registro.levelname == 'ERROR']


def test_escenarios_3d_comparten_escala_y_conservan_velocidades_independientes(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            (escena_a,) = user.find(ui.scene).elements
            (flujo_a,) = [o for o in escena_a.objects.values() if isinstance(o, AguaEnTuberia)]
            rapidez_a = flujo_a.rapidez
            user.find('Copiar A en B').click()
            await user.should_see('Resultados · Escenario B')
            (escena_b,) = user.find(ui.scene).elements
            (flujo_b,) = [o for o in escena_b.objects.values() if isinstance(o, AguaEnTuberia)]
            assert flujo_b.rapidez == rapidez_a
            (diametro,) = user.find(kind=ui.input, content='Diámetro interno D (mm)').elements
            with user:
                diametro.set_value('32')
            await user.should_see('Q  4.382 m³/h', retries=10)
            (flujo_b,) = [o for o in escena_b.objects.values() if isinstance(o, AguaEnTuberia)]
            assert 0 < flujo_b.rapidez < rapidez_a
            assert flujo_b.args[2] > flujo_a.args[2]
            user.find('Comparar A y B').click()
            assert len(user.find(ui.scene).elements) == 2

    asyncio.run(recorrido())
    assert not [registro for registro in caplog.records if registro.levelname == 'ERROR']


def test_volumen_inicial_reinicia_solo_trayectoria_3d(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            (escena,) = user.find(ui.scene).elements
            (llenado,) = [o for o in escena.objects.values() if isinstance(o, TanqueLlenado)]
            tiempo_anterior = llenado.trayectoria[-1][0]
            campos = user.find(kind=ui.input, content='Agua inicial (m³)').elements
            origen = next(campo for campo in campos if campo.value == '1.2')
            with user:
                origen.set_value('0,5')
            (nuevo,) = [o for o in escena.objects.values() if isinstance(o, TanqueLlenado)]
            assert nuevo.trayectoria[0][5] == pytest.approx(.5)
            assert nuevo.trayectoria[0][6] == pytest.approx(.2)
            assert nuevo.trayectoria[-1][0] < tiempo_anterior
            assert nuevo.trayectoria[-1][5] == pytest.approx(0)
            assert nuevo.trayectoria[-1][6] == pytest.approx(.7)
            assert nuevo.trayectoria[0][9] == pytest.approx(12)
            assert nuevo.trayectoria[-1][9] == pytest.approx(13)
            await user.should_see('3,765450 m³/h')  # punto estacionario inicial intacto
            with user:
                origen.set_value('2')
            await user.should_see('El volumen inicial debe estar entre 0 y la capacidad.')
            (detenido,) = [o for o in escena.objects.values() if isinstance(o, TanqueLlenado)]
            assert not detenido.activa

    asyncio.run(recorrido())
    assert not [registro for registro in caplog.records if registro.levelname == 'ERROR']
