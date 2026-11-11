"""Almacenamiento local de escenarios, incluidos borradores."""

import json
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path
from uuid import uuid4


RUTA_PREDETERMINADA = Path(__file__).resolve().parent.parent / "pumpcalc_data.sqlite3"


class AlmacenEscenarios:
    """Persiste configuraciones de escritorio, incluso antes de calcularlas."""

    def __init__(self, ruta=RUTA_PREDETERMINADA):
        self.ruta = Path(ruta)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._conexion()) as db, db:
            db.execute("""CREATE TABLE IF NOT EXISTS escenarios (
                id TEXT PRIMARY KEY, nombre TEXT NOT NULL, entradas TEXT NOT NULL,
                calculo TEXT, firma TEXT, actualizado TEXT NOT NULL
            )""")

    def _conexion(self):
        return sqlite3.connect(self.ruta)

    def guardar(self, escenario):
        """Crea un registro o actualiza el escenario identificado por su id."""
        # La firma permite reconocer resultados calculados con entradas anteriores.
        identificador = escenario.get("id") or str(uuid4())
        ahora = datetime.now().astimezone().isoformat(timespec="seconds")
        with closing(self._conexion()) as db, db:
            db.execute("""INSERT INTO escenarios(id,nombre,entradas,calculo,firma,actualizado)
                VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET
                nombre=excluded.nombre, entradas=excluded.entradas, calculo=excluded.calculo,
                firma=excluded.firma, actualizado=excluded.actualizado""",
                (identificador, escenario["nombre"], json.dumps(escenario["entradas"], ensure_ascii=False),
                 json.dumps(escenario.get("calculo"), ensure_ascii=False),
                 json.dumps(escenario.get("firma"), ensure_ascii=False), ahora))
        return identificador

    def listar(self):
        with closing(self._conexion()) as db:
            filas = db.execute("SELECT id,nombre,entradas,calculo,firma,actualizado FROM escenarios ORDER BY actualizado DESC").fetchall()
        return [self._escenario(fila) for fila in filas]

    def obtener(self, identificador):
        with closing(self._conexion()) as db:
            fila = db.execute("SELECT id,nombre,entradas,calculo,firma,actualizado FROM escenarios WHERE id=?", (identificador,)).fetchone()
        return self._escenario(fila) if fila else None

    @staticmethod
    def _escenario(fila):
        return {"id": fila[0], "nombre": fila[1], "entradas": json.loads(fila[2]),
                "calculo": json.loads(fila[3]) if fila[3] else None,
                "firma": json.loads(fila[4]) if fila[4] else None, "actualizado": fila[5]}
