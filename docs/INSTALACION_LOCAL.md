# Instalación y arranque local de PumpCalc

El paso 1 incorpora la vista inicial en NiceGUI. El cálculo, la animación y la comparación se añadirán en los pasos siguientes. El código anterior de escritorio se conserva como antecedente; `main.py` no es la entrada de la nueva aplicación y sus dependencias no forman parte del nuevo entorno.

## Entorno

- Python 3.13.7 en Windows.
- NiceGUI 4.0.0 y pytest 9.2.0, fijados en `requirements.txt`.

Desde la raíz de PumpCalc, en PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abre <http://127.0.0.1:8080> en el navegador. El servidor escucha únicamente en `127.0.0.1`. Para detenerlo, pulsa `Ctrl+C` en el terminal donde lo ejecutaste. No hace falta activar el entorno ni cambiar la política de ejecución de PowerShell.

Si prefieres activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
python app.py
```

Las pruebas numéricas de la nueva línea base comienzan en el paso 2. Su comando será:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Los tests heredados todavía corresponden a la versión anterior y no acreditan el modelo nuevo. Las comprobaciones efectivamente realizadas se registran en [avance.md](avance.md). El alcance final se describe en [README.md](README.md) y el orden de trabajo en el [plan de desarrollo](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md).
