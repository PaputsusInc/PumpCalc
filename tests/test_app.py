import tempfile
import tkinter as tk
import unittest
from pathlib import Path

import pytest

pytest.importorskip(
    "customtkinter",
    reason="Interfaz de escritorio heredada: CustomTkinter no forma parte del entorno NiceGUI.",
)

from pumpcalc.casos_uso import firma_calculo
from pumpcalc.persistencia import AlmacenEscenarios
from pumpcalc.ui.app import PumpCalcApp


class InterfazTests(unittest.TestCase):
    def test_calcular_guardar_duplicar_y_comparar(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as carpeta:
            try:
                app = PumpCalcApp(almacen=AlmacenEscenarios(Path(carpeta) / "escenarios.sqlite3"))
            except tk.TclError as error:
                self.skipTest(f"No hay pantalla para probar Tk: {error}")
            try:
                self.assertEqual(app._datos_actuales()["referencia"], "")
                self.assertNotIn("meta", app._datos_actuales())
                self.assertIn("longitud", app._datos_actuales())
                self.assertEqual(len(app.formulario.filas_curva), 5)
                curva_original = app._datos_actuales()["puntos"]
                app.formulario.agregar_punto("10", "2")
                self.assertIn("10; 2", app._datos_actuales()["puntos"])
                app.formulario.quitar_punto(app.formulario.filas_curva[-1])
                self.assertEqual(app._datos_actuales()["puntos"], curva_original)
                app.nombre_var.set("Original")
                app._calcular()
                app._guardar()
                original = app.almacen.listar()[0]
                app._duplicar(original)
                self.assertIsNone(app.escenario_id)
                self.assertFalse(app._vigente())
                app.variables["diametro"].set("40")
                app._guardar()
                guardado = app.almacen.obtener(app.escenario_id)
                self.assertNotEqual(guardado["firma"], firma_calculo(guardado["entradas"]))
                app._calcular()
                app._guardar()
                self.assertEqual(len(app.almacen.listar()), 2)
                app._abrir(original)
                self.assertTrue(app._vigente())
                app._mostrar_espacio("Escenarios")
                app._comparar()
                self.assertIn("Diámetro interior", app.texto_comparacion.get("1.0", "end"))
            finally:
                app.destroy()


if __name__ == "__main__":
    unittest.main()
