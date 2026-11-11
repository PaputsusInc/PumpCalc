# PumpCalc

Simulador web local en Python para explorar una bomba y una tubería entre dos depósitos abiertos. Permite editar la instalación y la curva de bomba, comparar A/B con animación 2D y consultar interpolación, Colebrook y bisección.

## Ejecutar en Windows

Versión verificada: Python 3.13.7. Desde la raíz del proyecto, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abre <http://127.0.0.1:8080>. El servidor escucha solo en `127.0.0.1`; `Ctrl+C` lo detiene. Las dependencias fijadas son NiceGUI 4.0.0 y pytest 9.2.0.

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Demostración

1. Revisa A: Q ≈ 3,765450 m³/h con D = 25 mm.
2. Pulsa **Copiar A en B**, cambia D a 32 mm y activa **Comparar A y B**.
3. B entrega Q ≈ 4,381752 m³/h y menor velocidad; A no alcanza la meta de 4 m³/h y B sí.
4. En B carga **Sin intersección** para ver el aviso y la escena detenida.

Los datos son ficticios. La animación es ilustrativa y no representa el llenado de tanques. Los resultados educativos no certifican una instalación real. A/B duran en memoria mientras la página permanece abierta; recargar restaura los ejemplos base.

## Documentación y comprobaciones

- [Manual, modelo y tutorial del motor](docs/README.md).
- [Guía de sustentación](docs/GUIA_SUSTENTACION.md).
- [Informe de verificación y pendientes](docs/VALIDACION_FINAL.md).
- [Registro de desarrollo](docs/avance.md).

La validación automatizada y la revisión visual en navegador real se registran por separado en el informe. `main.py` y los módulos de escritorio son antecedentes conservados; el arranque vigente es `app.py`.
