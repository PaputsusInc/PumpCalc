"""Integración de componentes y eventos con el simulador oficial de NiceGUI.

Estas pruebas no abren un navegador real ni acreditan la apariencia del SVG.
"""

import asyncio
from pathlib import Path

from nicegui import ui
from nicegui.testing.user_simulation import user_simulation


APP = Path(__file__).resolve().parents[1] / 'app.py'


def test_formulario_recalcula_y_retira_grafica_y_detalle_si_los_datos_son_invalidos(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            await user.should_see('3,765450 m³/h')
            (grafica,) = user.find(ui.echart).elements
            marcador = grafica.options['series'][-1]['data'][0]
            assert abs(marcador[0] - 3.765449524) < 1e-8
            assert len(grafica.options['series'][1]['data']) == 150
            await user.should_see('Iteraciones de bisección: 17.')
            (diametro,) = user.find(kind=ui.input, content='Diámetro interno D (mm)').elements
            with user:
                diametro.set_value('32')
            await asyncio.sleep(0.01)  # NiceGUI ejecuta los refrescos en segundo plano.
            await user.should_see('Cálculo pendiente', retries=1)
            await user.should_not_see(ui.echart, retries=1)
            await user.should_not_see('3,765450 m³/h', retries=1)
            await asyncio.sleep(0.1)
            await user.should_see('Cálculo pendiente', retries=1)
            await user.should_see('4,381752 m³/h', retries=10)
            (grafica,) = user.find(ui.echart).elements
            assert abs(grafica.options['series'][-1]['data'][0][0] - 4.381752014) < 1e-8
            with user:
                diametro.set_value('0')
            await user.should_see('Datos inválidos')
            assert diametro.props['error'] is True
            await user.should_not_see(ui.echart)
            await user.should_not_see(ui.expansion)
            user.find('Cargar caso base').click()
            await user.should_see('3,765450 m³/h')
            with user:
                diametro.set_value('32')
            user.find('Simular').click()
            await asyncio.sleep(0.01)
            await user.should_see('4,381752 m³/h', retries=1)
            (desnivel,) = user.find(kind=ui.input, content='Desnivel Δz (m)').elements
            with user:
                desnivel.set_value('40')
            await user.should_see('Ausencia de intersección', retries=10)
            (grafica,) = user.find(ui.echart).elements
            assert len(grafica.options['series']) == 3
            await user.should_not_see('4,381752 m³/h')

    asyncio.run(recorrido())
    assert not [registro for registro in caplog.records if registro.levelname == 'ERROR']


def test_tabla_edita_agrega_y_quita_filas_y_actualiza_el_dominio(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            user.find(marker='quitar-punto-6').click()
            await asyncio.sleep(0.01)
            await user.should_see('Cálculo pendiente', retries=1)
            await user.should_see('Solución encontrada', retries=10)
            (grafica,) = user.find(ui.echart).elements
            assert grafica.options['xAxis']['max'] == 4
            user.find('Agregar punto').click()
            await user.should_see('Datos inválidos')
            await user.should_not_see(ui.echart)
            (q,) = user.find(kind=ui.input, content='Caudal del punto 6').elements
            (h,) = user.find(kind=ui.input, content='Altura del punto 6').elements
            with user:
                q.set_value('5')
                h.set_value('10')
            await user.should_see('3,765450 m³/h', retries=10)
            (grafica,) = user.find(ui.echart).elements
            assert grafica.options['xAxis']['max'] == 5
            user.find('Cargar caso base').click()
            (q2,) = user.find(kind=ui.input, content='Caudal del punto 2').elements
            with user:
                q2.set_value('0')
            await user.should_see('Datos inválidos')
            assert q2.props['error'] is True
            await user.should_not_see(ui.echart)

    asyncio.run(recorrido())
    assert not [registro for registro in caplog.records if registro.levelname == 'ERROR']
