# Avance de desarrollo de PumpCalc

## Paso 1 Preparar el proyecto local

Fecha: 10 de noviembre de 2026, America/Bogota.

Resultado: entorno `.venv` creado con Python 3.13.7; NiceGUI 4.0.0 y pytest 9.2.0 fijados en `requirements.txt`. `app.py` muestra la vista inicial de PumpCalc en español y escucha en `127.0.0.1:8080`, sin recarga automática. `.gitignore` excluye `.venv`, `__pycache__` y `.pytest_cache`. Los módulos anteriores se conservan sin cambios.

Comprobaciones realizadas:

- `python -m venv .venv`: completado.
- Instalación de NiceGUI y pytest en `.venv`, seguida de `.venv\Scripts\python.exe -m pip install -r requirements.txt`: completada con las versiones fijadas.
- `.venv\Scripts\python.exe -m pip check`: `No broken requirements found.`
- `.venv\Scripts\python.exe -m pytest --version`: `pytest 9.2.0`. No se ejecutó la suite heredada ni se declara validado el motor nuevo; las pruebas numéricas comienzan en el paso 2.
- `.venv\Scripts\python.exe -m py_compile app.py`: sin errores.
- `.venv\Scripts\python.exe app.py`: `NiceGUI ready to go on http://127.0.0.1:8080`.
- Solicitud HTTP a `/`: estado 200 y contenido PumpCalc presente.
- Edge en modo headless con perfil temporal separado: captura de 1440 × 1000 inspeccionada; encabezado, bienvenida y textos visibles sin recortes. El navegador integrado y Computer Use fallaron al iniciar sus auxiliares por permisos del entorno; la comprobación visual se completó con Edge.

El servidor de comprobación se detiene al finalizar. Para abrirlo de nuevo, seguir [INSTALACION_LOCAL.md](INSTALACION_LOCAL.md).

Archivos previstos para el commit de este paso: `.gitignore`, `requirements.txt`, `app.py`, `docs/INSTALACION_LOCAL.md` y `docs/avance.md`. La reorganización y actualización documental previa, incluida la corrección de estado en `docs/README.md`, se mantiene fuera del área de preparación para no mezclar ese trabajo pendiente con el paso 1.

Commit registrado: `db16710` (`preparar la base local de PumpCalc`). Al retomar se comprobó que contiene exactamente los cinco archivos verificados del paso 1. Ya estaba registrado y no se duplicó.

## Paso 2 Validar entradas e interpolar la bomba

Fecha: 10 de noviembre de 2026, America/Bogota.

Resultado: `pumpcalc/entradas.py` define instalación, puntos, curva y escenario independientes de la interfaz, con objetos inmutables. Las funciones de entrada aceptan coma o punto decimal, distinguen campos vacíos de cero, rechazan datos no finitos y aplican los dominios de la sección 5. Las entradas visibles en mm y m³/h se convierten a m y m³/s. La meta opcional se valida por separado porque será común a A y B.

`pumpcalc/interpolacion.py` implementa la interpolación lineal por tramos en Python, admite nodos y extremos y rechaza extrapolación. `pumpcalc/ejemplos.py` conserva la curva ficticia y construye una configuración base independiente en cada llamada, con los valores de la sección 8. Todavía no se conecta el motor con el formulario ni se calculan pérdidas o punto de operación.

Comprobaciones realizadas con `.venv\Scripts\python.exe -m pytest`: **126 aprobadas y 1 módulo de pruebas omitido**. Las nuevas pruebas contienen 114 casos de validación, conversiones e interpolación; las 12 pruebas numéricas y de casos de uso heredados también pasan.

- Reproducción exacta de los seis nodos, incluidos ambos extremos; interpolación de los cinco tramos y referencia de 28,5 m en 2,5 m³/h.
- Dominio con caudal inicial positivo, tramo horizontal y rechazo de extrapolación y caudales no finitos.
- Límites de longitud, diámetro, desnivel, rugosidad, K, puntos y meta; L ≥ Δz y ε/D ≤ 0,05, incluidas sus fronteras.
- Entre 3 y 10 puntos; rechazo de duplicados, desorden y alturas crecientes sin alterar los datos de entrada.
- Conversiones del ejemplo base, coma y punto decimal, objetivo vacío frente a cero, errores con identificación de campo y fila, e independencia de las configuraciones de ejemplo.

La primera ejecución detectó que `tests/test_app.py`, de la interfaz de escritorio, impedía recoger las pruebas por la ausencia de CustomTkinter. Se conserva esa prueba y se añade una omisión explícita únicamente cuando falta esa dependencia heredada. No se omiten pruebas del motor nuevo. No cambió la interfaz web, por lo que este paso no requirió una nueva revisión en navegador.

Archivos preparados para este paso: `pumpcalc/entradas.py`, `pumpcalc/interpolacion.py`, `pumpcalc/ejemplos.py`, `tests/test_entradas.py`, `tests/test_interpolacion.py`, `tests/test_app.py`, `docs/INSTALACION_LOCAL.md` y `docs/avance.md`. Las fuentes y la reorganización documental previa permanecen fuera de este commit.

Commit propuesto: `feat: validar entradas e interpolar la curva de la bomba`. Pendiente de registrar al decir «sigamos», previa revisión de que no haya cambiado el contenido preparado. El siguiente paso es el 3, fricción y pérdidas hidráulicas.
