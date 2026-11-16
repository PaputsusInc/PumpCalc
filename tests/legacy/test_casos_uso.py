import tempfile
import unittest
from pathlib import Path

from pumpcalc.casos_uso import ErrorEntrada, calcular_escenario, firma_calculo, validar_entradas
from pumpcalc.persistencia import AlmacenEscenarios


def entradas(**cambios):
    datos = {
        "longitud": "40", "diametro": "32", "material": "PVC",
        "desnivel_vacio": "12", "desnivel_lleno": "15",
        "accesorio_0": "2", "accesorio_1": "1", "accesorio_2": "1",
        "modelo": "Bomba de prueba", "referencia": "Ficha de prueba",
        "unidad": "m³/h", "puntos": "0; 38\n2; 35\n4; 29\n6; 19\n8; 5",
    }
    datos.update(cambios)
    return datos


class CasosDeUsoTests(unittest.TestCase):
    def test_calcula_dos_condiciones_sin_meta_de_caudal(self):
        calculo = calcular_escenario(entradas())
        vacio = calculo["condiciones"]["vacio"]["resultado"]["caudal_m3h"]
        lleno = calculo["condiciones"]["lleno"]["resultado"]["caudal_m3h"]
        self.assertGreater(vacio, lleno)
        self.assertIn("Caudal estimado", calculo["resumen"])
        self.assertNotIn("meta", calculo["datos"])

    def test_la_distancia_modifica_el_caudal_calculado(self):
        corto = calcular_escenario(entradas(longitud="20"))
        largo = calcular_escenario(entradas(longitud="80"))
        self.assertGreater(corto["condiciones"]["vacio"]["resultado"]["caudal_m3h"],
                           largo["condiciones"]["vacio"]["resultado"]["caudal_m3h"])

    def test_identificacion_de_bomba_es_opcional(self):
        calculo = calcular_escenario(entradas(modelo="", referencia="", fabricante=""))
        self.assertIsNotNone(calculo["condiciones"]["vacio"]["resultado"])

    def test_convierte_unidad_antes_del_calculo(self):
        datos = validar_entradas(entradas(unidad="L/min", puntos="0; 38\n100; 19"))
        self.assertAlmostEqual(datos["puntos"][1][0], 6)
        datos = validar_entradas(entradas(unidad="US gpm", puntos="0; 38\n1; 19"))
        self.assertAlmostEqual(datos["puntos"][1][0], 0.22712472)

    def test_identifica_campo_con_error(self):
        with self.assertRaises(ErrorEntrada) as error:
            calcular_escenario(entradas(diametro="0"))
        self.assertEqual(error.exception.campo, "diametro")
        with self.assertRaises(ErrorEntrada) as error:
            calcular_escenario(entradas(puntos="0; 5\n1; 6"))
        self.assertEqual(error.exception.campo, "puntos")

    def test_sin_cruce_distingue_altura_insuficiente_de_curva_incompleta(self):
        bajo = calcular_escenario(entradas(puntos="0; 5\n2; 4"))
        self.assertEqual(bajo["condiciones"]["vacio"]["estado"], "altura_insuficiente")
        self.assertIn("No se pudo estimar", bajo["resumen"])
        corto = calcular_escenario(entradas(puntos="0; 38\n2; 35"))
        self.assertEqual(corto["condiciones"]["vacio"]["estado"], "sin_cruce")
        self.assertIn("No se pudo estimar", corto["resumen"])

    def test_firma_detecta_cambio_de_calculo_pero_no_de_nombre(self):
        inicial = entradas()
        modificado = entradas(longitud="70")
        self.assertNotEqual(firma_calculo(inicial), firma_calculo(modificado))
        modificado = entradas(meta="7")  # dato legado que ya no participa en el cálculo
        self.assertEqual(firma_calculo(inicial), firma_calculo(modificado))
        modificado = entradas(fabricante="Otro")
        self.assertEqual(firma_calculo(inicial), firma_calculo(modificado))

    def test_guarda_borrador_y_resultados(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as carpeta:
            almacen = AlmacenEscenarios(Path(carpeta) / "escenarios.sqlite3")
            datos = entradas()
            identificador = almacen.guardar({"nombre": "Borrador", "entradas": datos})
            self.assertIsNone(almacen.obtener(identificador)["calculo"])
            calculo = calcular_escenario(datos)
            almacen.guardar({"id": identificador, "nombre": "Calculado", "entradas": datos,
                             "calculo": calculo, "firma": firma_calculo(datos)})
            recuperado = almacen.obtener(identificador)
            self.assertEqual(recuperado["nombre"], "Calculado")
            self.assertEqual(recuperado["calculo"]["resumen"], calculo["resumen"])
            self.assertEqual(len(almacen.listar()), 1)


if __name__ == "__main__":
    unittest.main()
