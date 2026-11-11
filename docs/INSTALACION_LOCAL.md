# Instalación y arranque local de PumpCalc

La aplicación usa NiceGUI y el motor verificado hasta el paso 4. El paso 5 añade formulario y resultados de un escenario; su revisión interactiva en navegador sigue pendiente, como se registra en [avance.md](avance.md). La animación y la comparación se incorporan en pasos posteriores. El código anterior de escritorio se conserva como antecedente; `main.py` no es la entrada de la nueva aplicación y sus dependencias no forman parte del nuevo entorno.

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

Desde el paso 2, las pruebas de validación e interpolación de la nueva línea base se ejecutan con:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Las pruebas numéricas heredadas se conservan como comprobación de la versión anterior. La prueba de interfaz de escritorio se omite explícitamente si no está instalado CustomTkinter, que no forma parte de las dependencias de la aplicación web. Esa omisión no corresponde a la interfaz NiceGUI. Las comprobaciones efectivamente realizadas se registran en [avance.md](avance.md). El alcance final se describe en [README.md](README.md) y el orden de trabajo en el [plan de desarrollo](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md).
