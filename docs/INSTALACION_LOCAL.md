# Instalación y arranque local de PumpCalc

La aplicación usa NiceGUI y el motor hidráulico verificado. Hasta el paso 8 incorpora escenarios A/B independientes, resultados, curvas, detalle numérico, animaciones y meta común. Los eventos y componentes se comprueban con el simulador oficial de NiceGUI; la revisión visual en un navegador real sigue pendiente, como se registra en [avance.md](avance.md). El código anterior de escritorio se conserva como antecedente; `main.py` no es la entrada de la nueva aplicación y sus dependencias no forman parte del nuevo entorno.

## Entorno

Al iniciar se calcula el caso base y se actualizan sus trazas de agua según la velocidad del motor. **Pausar animación** detiene solo el movimiento; **Reanudar animación** lo continúa. Editar invalida el resultado y suspende las trazas hasta recalcular. Una configuración sin cruce muestra la instalación detenida y su aviso.

Selecciona **A** o **B** para editar; **Copiar A en B** crea una copia independiente y abre B. Elige un ejemplo y pulsa **Cargar ejemplo** para aplicarlo solo al activo. **Comparar A y B** muestra ambas escenas, sus datos y las curvas superpuestas. La meta de caudal es opcional y común; muestra el margen y distingue cumplimiento, incumplimiento y límite numérico, sin cambiar el punto de operación. Recargar la página restaura ambos casos base y la meta de demostración de 4 m³/h.

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

Comprueba las dependencias y ejecuta la suite completa con:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest
```

El 11 de noviembre de 2026 se repitieron instalación, pruebas y arranque en un entorno nuevo, `.tmp\entrega-limpia-20261111`: 282 pruebas aprobadas, 1 módulo heredado omitido y respuesta HTTP 200. La revisión visual sigue pendiente porque el host del navegador integrado no está disponible. Consulta el [informe de verificación](VALIDACION_FINAL.md) para los resultados y el recorrido pendiente, y la [guía de sustentación](GUIA_SUSTENTACION.md) para demostrar los ejemplos.

Las pruebas numéricas heredadas se conservan como comprobación de la versión anterior. La prueba de interfaz de escritorio se omite explícitamente si no está instalado CustomTkinter, que no forma parte de las dependencias de la aplicación web. Esa omisión no corresponde a la interfaz NiceGUI. Las comprobaciones efectivamente realizadas se registran en [avance.md](avance.md). El alcance final se describe en [README.md](README.md) y el orden de trabajo en el [plan de desarrollo](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md).
