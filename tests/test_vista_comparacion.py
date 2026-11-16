"""Recorridos A/B y meta común con el simulador oficial de NiceGUI."""

import asyncio
import base64
from pathlib import Path

from nicegui import ui
from nicegui.testing.user_simulation import user_simulation


APP = Path(__file__).resolve().parents[1] / 'app.py'


def test_recorrido_copiar_modificar_comparar_y_cambiar_meta_sin_recalcular(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            user.find(marker='selector-vista').elements.pop().set_value('2D')
            user.find('Copiar A en B').click()
            await user.should_see('Resultados · Escenario B')
            (diametro,) = user.find(kind=ui.input, content='Diámetro interno D (mm)').elements
            with user:
                diametro.set_value('32')
            await user.should_see('B: Alcanza la meta en el modelo', retries=10)
            await user.should_see('A: No alcanza la meta en el modelo')
            user.find('Comparar A y B').click()
            await user.should_see('Comparación de escenarios A y B')
            imagenes = user.find(ui.interactive_image).elements
            assert len(imagenes) == 2
            fondos = [base64.b64decode(i.source.split(',', 1)[1]).decode('utf-8') for i in imagenes]
            assert any('D = 25,00 mm' in f for f in fondos)
            assert any('D = 32,00 mm' in f for f in fondos)
            (grafica,) = user.find(ui.echart).elements
            assert len(grafica.options['series']) == 8
            (objetivo,) = user.find(kind=ui.input, content='Caudal objetivo común (m³/h, opcional)').elements
            with user:
                objetivo.set_value('5')
            await user.should_see('B: No alcanza la meta en el modelo')
            assert user.find(ui.interactive_image).elements == imagenes
            assert user.find(ui.echart).elements == {grafica}
            with user.scope(marker='escena-A'):
                user.find('Pausar animación').click()
            with user.scope(marker='escena-B'):
                await user.should_see('Visualización vinculada a la velocidad calculada.')
            (selector,) = user.find(marker='selector-escenario').elements
            with user:
                selector.set_value('A')
            await user.should_see('Resultados · Escenario A')
            assert diametro.value == '25'
            user.find('Comparar A y B').click()
            await asyncio.sleep(0.01)
            assert len(user.find(ui.interactive_image).elements) == 1

    asyncio.run(recorrido())
    assert not [r for r in caplog.records if r.levelname == 'ERROR']


def test_cargar_ejemplo_en_b_sin_cruce_y_recargar_restaura_el_estado(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            (selector,) = user.find(marker='selector-escenario').elements
            with user:
                selector.set_value('B')
            await user.should_see('Resultados · Escenario B')
            (ejemplo,) = user.find(kind=ui.select, content='Ejemplo').elements
            with user:
                ejemplo.set_value('sin_interseccion')
            user.find('Cargar ejemplo').click()
            await user.should_see('Ausencia de intersección')
            user.find('Comparar A y B').click()
            await user.should_see('Comparación de caudal no disponible: faltan resultados vigentes en A o B.')
            (grafica,) = user.find(ui.echart).elements
            assert len(grafica.options['series']) == 7
            await user.open('/')
            user.find(marker='selector-vista').elements.pop().set_value('2D')
            await user.should_see('Resultados · Escenario A')
            (diametro,) = user.find(kind=ui.input, content='Diámetro interno D (mm)').elements
            assert diametro.value == '25'
            assert len(user.find(ui.interactive_image).elements) == 1

    asyncio.run(recorrido())
    assert not [r for r in caplog.records if r.levelname == 'ERROR']


def test_cambio_de_activo_no_desvia_el_recalculo_pendiente(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            (diametro,) = user.find(kind=ui.input, content='Diámetro interno D (mm)').elements
            (selector,) = user.find(marker='selector-escenario').elements
            with user:
                diametro.set_value('32')
                selector.set_value('B')
            await user.should_see('Resultados · Escenario B')
            await asyncio.sleep(0.25)
            await user.should_see('A: Alcanza la meta en el modelo')
            await user.should_see('B: No alcanza la meta en el modelo')
            assert diametro.value == '25'

    asyncio.run(recorrido())
    assert not [r for r in caplog.records if r.levelname == 'ERROR']


def test_datos_generales_de_bomba_pertenecen_al_escenario_y_no_recalculan(caplog):
    async def recorrido():
        async with user_simulation(main_file=APP) as user:
            await user.open('/')
            (potencia,) = user.find(kind=ui.input, content='Potencia (HP)').elements
            (altura,) = user.find(kind=ui.input, content='Hmax (m)').elements
            (caudal,) = user.find(kind=ui.input, content='Qmax (m³/h)').elements
            with user:
                potencia.set_value('1,5')
                altura.set_value('35')
                caudal.set_value('6')
            await user.should_see('3,765450 m³/h')
            user.find('Copiar A en B').click()
            await user.should_see('Resultados · Escenario B')
            assert (potencia.value, altura.value, caudal.value) == ('1,5', '35', '6')
            with user:
                potencia.set_value('2')
            (selector,) = user.find(marker='selector-escenario').elements
            with user:
                selector.set_value('A')
            await user.should_see('Resultados · Escenario A')
            assert potencia.value == '1,5'
            user.find('Comparar A y B').click()
            await user.should_see('Comparación de escenarios A y B')
            with user.scope(marker='comparacion'):
                (tabla,) = user.find(ui.table).elements
            fila_potencia = next(f for f in tabla.rows if f['dato'] == 'Potencia del motor (HP)')
            assert (fila_potencia['A'], fila_potencia['B']) == ('1,5', '2')

    asyncio.run(recorrido())
    assert not [r for r in caplog.records if r.levelname == 'ERROR']
