"""Eventos y temporizador de animación con el simulador oficial de NiceGUI."""

import asyncio
import base64
from pathlib import Path

from nicegui import ui
from nicegui.testing.user_simulation import user_simulation


APP = Path(__file__).resolve().parents[1] / 'app.py'


def fondo(imagen):
    return base64.b64decode(imagen.source.split(',', 1)[1]).decode('utf-8')


def test_temporizador_mueve_solo_trazas_pausa_reanuda_y_se_detiene_con_error(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            (imagen,) = user.find(ui.interactive_image).elements
            (grafica,) = user.find(ui.echart).elements
            fuente_inicial, trazas_iniciales = imagen.source, imagen.content
            await asyncio.sleep(0.12)
            assert imagen.content != trazas_iniciales
            assert imagen.source == fuente_inicial
            assert user.find(ui.echart).elements == {grafica}
            await user.should_see('3,765450 m³/h')
            user.find('Pausar animación').click()
            pausadas = imagen.content
            await asyncio.sleep(0.12)
            assert imagen.content == pausadas
            await user.should_see('Animación pausada. El resultado hidráulico se mantiene.')
            await user.should_see('3,765450 m³/h')
            user.find('Reanudar animación').click()
            await asyncio.sleep(0.12)
            assert imagen.content != pausadas
            (diametro,) = user.find(kind=ui.input, content='Diámetro interno D (mm)').elements
            with user:
                diametro.set_value('0')
            await user.should_see('Movimiento suspendido: datos inválidos.')
            detenidas = imagen.content
            await asyncio.sleep(0.12)
            assert imagen.content == detenidas
            assert 'Q = — m³/h' in fondo(imagen)
            user.find('Cargar caso base').click()
            await user.should_see('3,765450 m³/h')
            (desnivel,) = user.find(kind=ui.input, content='Desnivel Δz (m)').elements
            with user:
                desnivel.set_value('40')
            await user.should_see('Movimiento suspendido: cálculo pendiente.', retries=1)
            detenidas = imagen.content
            await asyncio.sleep(0.1)
            assert imagen.content == detenidas
            await user.should_see('Movimiento suspendido: ausencia de intersección.', retries=10)
            detenidas = imagen.content
            await asyncio.sleep(0.12)
            assert imagen.content == detenidas
            assert 'Q = — m³/h' in fondo(imagen)

    asyncio.run(recorrido())
    assert not [r for r in caplog.records if r.levelname == 'ERROR']


def test_cambio_de_diametro_sincroniza_escena_y_resultados_sin_recrear_imagen(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            (imagen,) = user.find(ui.interactive_image).elements
            assert 'D = 25,00 mm' in fondo(imagen)
            (diametro,) = user.find(kind=ui.input, content='Diámetro interno D (mm)').elements
            with user:
                diametro.set_value('32')
            await user.should_see('4,381752 m³/h', retries=10)
            assert user.find(ui.interactive_image).elements == {imagen}
            svg = fondo(imagen)
            assert 'D = 32,00 mm' in svg
            assert 'Q = 4,381752 m³/h' in svg
            assert 'v = 1,513406 m/s' in svg

    asyncio.run(recorrido())
    assert not [r for r in caplog.records if r.levelname == 'ERROR']
