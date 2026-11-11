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

Commit registrado: `f7236f1` (`feat: validar entradas e interpolar la curva de la bomba`). Al retomar el paso 3 ya estaba registrado y el árbol de trabajo estaba limpio; no se duplicó. Ese commit incluye también la reorganización documental y los archivos de `Baseline y pasos` que anteriormente permanecían pendientes.

## Paso 3 Calcular las pérdidas hidráulicas

Fecha: 10 de noviembre de 2026, America/Bogota.

Resultado: `pumpcalc/friccion.py` implementa el factor de Darcy con f = 64/Re en flujo laminar, interpolación didáctica en transición y Colebrook por punto fijo en turbulencia. Se inicia con x₀ = 1/√0,02, con límite de 100 iteraciones y parada que exige simultáneamente cambio y residuo absolutos ≤ 10⁻¹⁰. Cada iteración conserva x anterior, x nuevo, cambio y residuo. En transición la traza identifica el cálculo auxiliar en Re = 4000 y se devuelve una advertencia de aproximación.

`pumpcalc/perdidas.py` calcula área, velocidad, Reynolds, pérdidas en tubería y accesorios y Hs = Δz + hf + hK. Usa g = 9,81 m/s² y ν = 1,004 × 10⁻⁶ m²/s. En Q = 0 no evalúa fricción: v, Re y pérdidas son cero, Hs = Δz y f es no aplicable. Los fallos de Colebrook se propagan como `ErrorConvergencia`, sin sustituir el factor por una aproximación silenciosa.

Comprobaciones realizadas con `.venv\Scripts\python.exe -m pytest`: **170 aprobadas y 1 módulo heredado de interfaz omitido** por ausencia de CustomTkinter. Las 44 pruebas nuevas de fricción y pérdidas verifican:

- f = 0,064 en Re = 1000 y f ≈ 0,018513866077 en Re = 100000, ε/D = 0,0001, con error absoluto ≤ 10⁻⁹.
- Convergencia en los extremos del dominio turbulento del sandbox, para ε/D = 0 y 0,05; iterados entre 3 y 20 y ambos criterios de parada satisfechos.
- Continuidad del factor y de Hs en Re = 2000 y 4000; traza auxiliar y advertencia en transición.
- Caudal cero sin llamar a fricción, pérdida laminar contrastada con Poiseuille, participación de longitud, rugosidad, diámetro y K sin coeficientes ocultos.
- Falta de convergencia forzada con una iteración, tanto en transición como en turbulencia, y propagación del fallo al evaluar el sistema.

Evaluación observada para el caso base al caudal tabulado Q = 3,765443 m³/h: v = 2,130804858 m/s, Re = 53057,889896, f = 0,020839985678, hf = 7,716240448 m, hK = 0,925653281 m y Hs = 20,641893730 m. Colebrook empleó 11 iteraciones; cambio final ≈ 9,47 × 10⁻¹¹ y residuo ≈ −1,13 × 10⁻¹¹. Reynolds se compara con el valor aproximado 53057,90 de la fuente con tolerancia absoluta de 0,02; los valores de Q y las referencias están redondeados. Aquí se evalúa un caudal suministrado: la búsqueda del punto de operación corresponde al paso 4.

Archivos preparados: `pumpcalc/friccion.py`, `pumpcalc/perdidas.py`, `tests/test_friccion.py`, `tests/test_perdidas.py` y `docs/avance.md`. No cambió la interfaz web, por lo que no fue necesaria una nueva revisión en navegador.

Commit registrado: `09e841c` (`feat: calcular fricción y pérdidas hidráulicas`). Al retomar el paso 4 ya estaba registrado y el árbol de trabajo estaba limpio; no se duplicó.

## Paso 4 Resolver y verificar el punto de operación

Fecha: 10 de noviembre de 2026, America/Bogota.

Resultado: `pumpcalc/biseccion.py` implementa un solver independiente del modelo hidráulico. Acepta raíces exactas en extremos o punto medio, comprueba el cambio de signo y guarda a, b, c, F(c) y semiancho antes de dividir cada intervalo. La parada normal exige simultáneamente semiancho ≤ 10⁻⁷ m³/s y residuo absoluto ≤ 10⁻⁴ m, con máximo de 80 iteraciones. Los parámetros son configurables desde Python para las pruebas. Si se agota el límite, devuelve falta de convergencia y no presenta una raíz como solución.

`pumpcalc/operacion.py` integra interpolación y pérdidas y resuelve F(Q) = Hb(Q) − Hs(Q) exactamente en el dominio ingresado de la bomba. Devuelve estado, mensaje, punto de operación, tramo interpolado y evidencia de bisección. El punto incluye los datos del sistema y la traza de fricción únicamente de la evaluación final. Distingue ambos casos sin cambio de signo y los fallos de bisección o Colebrook. La ausencia de solución se expresa con punto ausente, no con Q = 0.

Comprobación ejecutada: `.venv\Scripts\python.exe -m pytest` → **207 aprobadas y 1 módulo heredado de interfaz omitido** por ausencia de CustomTkinter. Las 37 pruebas nuevas cubren la raíz analítica √21 − 1 con tolerancias de 10⁻⁶ para variable y residuo, cotas y trazas, raíces en extremos y nodo interior, dominios que empiezan por encima de cero, ambos signos sin cruce y agotamiento de iteraciones. Se verifican también la propagación del fallo de Colebrook y una solución válida con Q = 0, distinta de ausencia de cruce.

Resultados observados con los parámetros predeterminados:

| Caso | Q en m³/h | H de bomba en m | Iteraciones | Residuo en m | Cota de Q en m³/s |
| --- | --- | --- | --- | --- | --- |
| A base | 3,765449524 | 20,641853333 | 17 | −0,000067489 | 1,059638 × 10⁻⁸ |
| B diámetro de 32 mm | 4,381752014 | 15,564231873 | 17 | 0,000066667 | 1,059638 × 10⁻⁸ |
| Longitud de 80 m | 3,227949142 | 24,404356003 | 19 | −0,000026510 | 2,649095 × 10⁻⁹ |
| Desnivel de 40 m | No aplica | No aplica | 0 | No aplica | No aplica |

Los tres puntos cumplen errores absolutos máximos de 0,001 m³/h en Q y 0,001 m en H frente a las referencias de la fuente, además de las dos condiciones internas de parada. El factor de Darcy del caso base cumple el error absoluto máximo de 10⁻⁷. Con Δz = 40 m se informa que la curva de bomba queda por debajo de la del sistema en el intervalo disponible. No se extrapola ni se afirma qué ocurre fuera de los datos.

Archivos preparados: `pumpcalc/biseccion.py`, `pumpcalc/operacion.py`, `tests/test_biseccion.py`, `tests/test_operacion.py` y `docs/avance.md`. La interfaz web sigue mostrando la vista inicial; este paso verifica el motor y no requiere revisión nueva en navegador.

Commit propuesto: `feat: resolver el punto de operación por bisección`. Pendiente de registrar al decir «sigamos», previa revisión del contenido preparado. El siguiente paso es el 5, conectar el formulario y los resultados de un escenario.
