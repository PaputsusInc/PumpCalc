import unittest

from pumpcalc.hydraulics import altura_instalacion, punto_operacion


class PumpCalcNumericalTests(unittest.TestCase):
    def setUp(self):
        self.curva = [(0, 38), (2, 35), (4, 29), (6, 19), (8, 5)]

    def test_el_cruce_iguala_ambas_alturas_dentro_de_la_curva(self):
        resultado = punto_operacion(self.curva, 40, 32, 150, 12, 4.45)
        self.assertIsNotNone(resultado)
        self.assertGreaterEqual(resultado["caudal_m3h"], self.curva[0][0])
        self.assertLessEqual(resultado["caudal_m3h"], self.curva[-1][0])
        self.assertAlmostEqual(resultado["altura_bomba_m"], resultado["total_m"], places=6)

    def test_no_extrapola_si_no_hay_cruce(self):
        self.assertIsNone(punto_operacion([(0, 5), (2, 4)], 40, 32, 150, 12, 4.45))

    def test_aumentar_diametro_aumenta_el_caudal_estimado(self):
        pequeno = punto_operacion(self.curva, 40, 25, 150, 12, 4.45)
        grande = punto_operacion(self.curva, 40, 40, 150, 12, 4.45)
        self.assertGreater(grande["caudal_m3h"], pequeno["caudal_m3h"])

    def test_caudal_cero_no_produce_perdidas(self):
        resultado = altura_instalacion(0, 40, 32, 150, 12, 4.45)
        self.assertEqual(resultado["tuberia_m"], 0)
        self.assertEqual(resultado["accesorios_m"], 0)
        self.assertEqual(resultado["total_m"], 12)


if __name__ == "__main__":
    unittest.main()
