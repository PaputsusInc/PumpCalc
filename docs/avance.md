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

Commit registrado: `1c7ef04` (`feat: resolver el punto de operación por bisección`). Al retomar el paso 5 ya estaba registrado y el árbol de trabajo estaba limpio; no se duplicó.

## Paso 5 Conectar el formulario y los resultados

Estado: implementación y pruebas automatizadas verificadas. La comprobación interactiva en navegador permanece pendiente. El usuario autorizó explícitamente registrar el commit y continuar con el paso 6 con esa limitación documentada.

`app.py` carga una vista NiceGUI en español con campos de instalación, tabla editable de 3 a 10 puntos de bomba, Simular, Cargar caso base e indicadores de un escenario. `pumpcalc/simulacion.py` mantiene entradas y estado por sesión; editar retira el resultado anterior y valida inmediatamente. La vista programa el recálculo mediante un temporizador de 200 ms para entradas válidas; las revisiones antiguas se descartan. Simular cancela el temporizador y calcula inmediatamente. Se presentan los estados de datos inválidos, pendiente, solución, ausencia de intersección y falta de convergencia.

Comprobaciones realizadas:

- `.venv\Scripts\python.exe -m pytest`: **216 aprobadas y 1 módulo heredado de interfaz omitido** por ausencia de CustomTkinter. Las 9 pruebas nuevas de sesión cubren invalidación, rechazo de llamadas diferidas antiguas, errores por campo y celda, recarga del caso base, edición de puntos, límites de cantidad, independencia de sesiones y estados sin solución o sin convergencia.
- `.venv\Scripts\python.exe -m py_compile app.py pumpcalc/vista.py pumpcalc/simulacion.py`: sin errores.
- `.venv\Scripts\python.exe app.py`: servidor iniciado en `http://127.0.0.1:8080`.
- Solicitud HTTP a `/`: estado 200; formulario y resultado base `3,765450` presentes en la respuesta.

La comprobación interactiva quedó bloqueada: Computer Use indicó que no pudo determinar con suficiente confianza la URL del navegador de Windows para aplicar su política y detuvo el acceso. No se continuó la automatización del navegador ni se declara verificada la interacción, el temporizador o el aspecto visual. El servidor de prueba se detuvo al finalizar.

Commit registrado por instrucción explícita del usuario: `289f5da` (`feat: conectar entradas y simulación de un escenario`). La comprobación visual en un navegador real sigue pendiente. Durante el paso 6 se añadieron pruebas de integración del simulador oficial de NiceGUI para verificar los eventos y componentes del formulario, sin presentar esas pruebas como observación visual.

## Paso 6 Dibujar las curvas y explicar el cálculo

Fecha: 10 de noviembre de 2026, America/Bogota.

Estado: implementación y verificación automatizada completas; revisión visual en navegador real pendiente por indisponibilidad del host de acceso al navegador integrado.

Resultado: `pumpcalc/presentacion.py` prepara las opciones de `ui.echart`, los datos de 150 muestras de Hs y las tablas numéricas sin depender de los controles. La bomba se dibuja uniendo sus nodos por segmentos exactos, sin suavizado que cambie la interpolación. Ambos ejes son numéricos, Q en m³/h y H en m, con leyenda y puntos identificados. El marcador usa exactamente Q y H del solver, con independencia de las muestras gráficas. Las curvas conservan el dominio de la bomba, incluso cuando empieza por encima de cero; sin cruce se mantienen sin inventar un marcador.

`pumpcalc/detalle.py` muestra un panel desplegable con las tolerancias, total de iteraciones, residuo, cota y tabla de bisección. Los caudales, intervalos y semianchos se convierten a m³/h solo para presentar; los residuos se mantienen en metros. Incluye el tramo interpolado y la explicación de fricción: sin iteración para laminar, factor no aplicable en Q = 0 y traza de punto fijo exclusivamente del resultado final en turbulencia o del auxiliar f₄₀₀₀ en transición.

Las pruebas de integración detectaron un fallo al eliminar filas: el temporizador intentaba crearse dentro de la fila eliminada. Se corrigió asociándolo a la página y esperando el refresco de la tabla antes de validar sus controles nuevos. Se mantiene la retirada de gráfica, cifras y detalle cuando las entradas son pendientes o inválidas.

Comprobaciones realizadas:

- `.venv\Scripts\python.exe -m pytest`: **235 aprobadas y 1 módulo heredado de interfaz omitido** por ausencia de CustomTkinter. Se añadieron 17 casos de presentación y 2 recorridos con el simulador oficial de NiceGUI.
- Las pruebas de presentación verifican 150 muestras, ejes y dominios, segmentos y nodos de la bomba, marcador independiente del muestreo, ambos casos sin cruce, tablas de bisección, trazas de fricción por régimen y Q = 0.
- Los recorridos simulados verifican el caso base, el recálculo tras 200 ms, ausencia de cálculo a los 100 ms, cambio D = 32 mm, Simular inmediato, Cargar caso base, retirada de resultados inválidos, error junto al campo o celda, agregar/quitar puntos, actualización del dominio y curvas sin marcador para Δz = 40 m. No se registraron errores de NiceGUI en los recorridos.
- `python -m py_compile` sobre los tres módulos de presentación: sin errores.
- Inicio de la versión final mediante `.venv\Scripts\python.exe app.py`; solicitud HTTP a `/` con estado 200 y presencia de formulario, gráfica, marcador, resultado base y detalle numérico. El servidor de comprobación se detuvo al finalizar.
- El intento de abrir `http://127.0.0.1:8080` en el navegador integrado devolvió `The browser access host is unavailable`. No se comprobó el dibujo SVG real, el tamaño o la disposición visual. Las pruebas de usuario simulado no abren un navegador ni sustituyen esa revisión visual.

Archivos preparados: `pumpcalc/vista.py`, `pumpcalc/presentacion.py`, `pumpcalc/detalle.py`, `tests/test_presentacion.py`, `tests/test_vista.py`, `docs/README.md`, `docs/INSTALACION_LOCAL.md` y `docs/avance.md`.

Commit registrado: `a5952b9` (`curvas, marcador del punto de operación y detalle de bisección y colebrook`). Al retomar el paso 7 ya estaba registrado y el árbol de trabajo estaba limpio; no se duplicó. La comprobación visual pendiente debe retomarse cuando esté disponible el navegador.

## Paso 7 Animar el agua en la instalación

Fecha: 10 de noviembre de 2026, America/Bogota.

Estado: implementación y verificación automatizada completas; revisión visual en navegador real pendiente por indisponibilidad del host de acceso al navegador integrado.

Resultado: `pumpcalc/animacion.py` genera un esquema SVG con depósitos de niveles fijos, bomba y tubería llena. Las etiquetas incluyen L, D, Δz, Q y v. El grosor aumenta con el diámetro mediante una escala visual creciente; el esquema declara que no está a escala geométrica. Las 16 trazas siguen la línea de tubería desde origen a destino y retornan al comienzo del recorrido. Su avance usa el tiempo real transcurrido y s(v) = 240v/(v+2), común a todas las configuraciones, con v calculada por el motor.

`pumpcalc/escena.py` incorpora `ui.interactive_image` con fondo SVG de instalación y una capa de trazas. Un `ui.timer` a 30 actualizaciones por segundo cambia únicamente el contenido de las trazas; no recalcula la hidráulica ni reconstruye las curvas o el formulario. Cambiar las entradas actualiza la escena con el resultado vigente y suspende el movimiento mientras esté pendiente o sea inválido, sin cruce o sin convergencia. Una solución válida con Q = 0 permanece sin movimiento y conserva ese significado. Pausar y reanudar afecta solo al estado visual, sin cambiar el punto de operación ni acumular desplazamiento durante la pausa.

Comprobaciones realizadas:

- `.venv\Scripts\python.exe -m pytest`: **259 aprobadas y 1 módulo heredado de interfaz omitido** por ausencia de CustomTkinter. Se añadieron 22 casos de escala, geometría y movimiento y 2 recorridos de integración con el simulador oficial de NiceGUI.
- Se comprobaron s(0) = 0, monotonía y límite visual, equivalencia de avance para distintos tamaños de fotograma, pausa y reanudación, suspensión en los cuatro estados sin solución vigente, solución válida en Q = 0 y recorrido de las trazas por ambos codos.
- Se verificó que el fondo contiene las etiquetas del resultado y mantiene los niveles de los depósitos, que la capa móvil solo contiene trazas y que los fotogramas cambian esa capa sin modificar el fondo ni recrear la gráfica.
- Para A se observaron v = 2,130808550 m/s, s = 123,799988746 px/s y grosor = 23,863137139 px. Con D = 32 mm se observaron v = 1,513406017 m/s, s = 103,380435472 px/s y grosor = 28,136862861 px. La tubería aumenta su grosor y el avance visual disminuye mientras Q aumenta, con la misma escala para ambos casos.
- Las pruebas de integración verificaron pausa sin cambiar Q, reanudación, suspensión por dato inválido, cálculo pendiente y falta de cruce, y actualización de Q, v y D sin recrear la imagen.
- `.venv\Scripts\python.exe -m py_compile pumpcalc/animacion.py pumpcalc/escena.py pumpcalc/vista.py`: sin errores.
- La aplicación inició mediante `python app.py`; la respuesta HTTP de `/` tuvo estado 200 y contenía escena, Pausar animación, Movimiento ilustrativo y resultado base. El servidor de comprobación se detuvo al finalizar.
- El intento de abrir la vista local en el navegador integrado devolvió `The browser access host is unavailable`. No se declara comprobado visualmente el movimiento, el grosor o la disposición en un navegador real.

Archivos preparados: `pumpcalc/animacion.py`, `pumpcalc/escena.py`, `pumpcalc/vista.py`, `tests/test_animacion.py`, `tests/test_escena.py`, `docs/README.md`, `docs/INSTALACION_LOCAL.md` y `docs/avance.md`.

Commit registrado: `80ad072` (`feat: animar el flujo de agua según la velocidad calculada`). Al retomar el paso 8 ya estaba registrado; no se duplicó. La comprobación visual pendiente debe retomarse cuando esté disponible el navegador.

## Paso 8 Comparar escenarios y probar una meta

Fecha: 11 de noviembre de 2026, America/Bogota.

Estado: implementación y verificación automatizada completas; revisión visual en navegador real pendiente por indisponibilidad del host de acceso al navegador integrado.

Resultado: `pumpcalc/comparacion.py` conserva sesiones A y B independientes en memoria y una meta opcional común. Copiar A en B duplica entradas, estado, resultado y trazas; cada edición invalida únicamente su escenario. Los temporizadores capturan el escenario y su revisión, de modo que cambiar el selector no desvía un cálculo pendiente hacia otro caso. Recargar la página crea de nuevo las dos configuraciones base y la meta de 4 m³/h.

La vista permite seleccionar A o B, copiar A en B y cargar caso base, diámetro de 32 mm o ausencia de intersección en el activo. La comparación muestra dos escenas con la misma escala de velocidad y grosor, una tabla de entradas y resultados y curvas superpuestas con dominios propios. Presenta cambio B − A, diferencia absoluta y porcentaje respecto de A; si Q de A es cero el porcentaje es no aplicable. Si faltan resultados vigentes no inventa una comparación numérica ni un marcador.

La meta se valida aparte. Su margen es Q − objetivo y se compara con la cota numérica del solver para distinguir En el límite numérico, Alcanza la meta en el modelo y No alcanza la meta en el modelo. Editar únicamente el objetivo no modifica entradas, revisiones, resultados, escenas ni curvas; solo actualiza la evaluación y sus mensajes. Una meta vacía significa ausencia de referencia y una meta inválida se señala junto al campo.

Comprobaciones realizadas:

- `.venv\Scripts\python.exe -m pytest`: **282 aprobadas y 1 módulo heredado de interfaz omitido** por ausencia de CustomTkinter. Se añadieron 20 casos del modelo y la gráfica de comparación y 3 recorridos del simulador oficial de NiceGUI.
- Las pruebas verifican copias independientes de entradas, filas, resultados y trazas; edición de B con A intacto; tres ejemplos solo en el activo; meta opcional e inválida; márgenes dentro de la cota; ausencia de comparación para estados sin resultado; porcentaje no aplicable con Q de A cero; dominios propios y marcadores solo donde hay solución.
- Los recorridos simulados verifican copiar A, editar D de B a 32 mm, comparar dos escenas y ocho series, cambiar la meta sin recrear la gráfica o las imágenes, pausar A sin detener B, cargar en B el ejemplo sin cruce, recargar la página y cambiar de activo durante un cálculo pendiente. No se registraron errores de NiceGUI.
- Con la meta de 4 m³/h, A mostró margen −0,234550476 m³/h y B margen +0,381752014 m³/h. El cambio B − A fue +0,616302490 m³/h, equivalente a +16,367301867 % respecto de A. A no alcanza la meta y B sí.
- Compilación de los siete módulos modificados o añadidos de aplicación con `python -m py_compile`: sin errores.
- La aplicación inició con `python app.py`; la solicitud HTTP a `/` devolvió estado 200 y los controles A/B, meta, ejemplo y resultado base. El servidor de comprobación se detuvo al finalizar.
- El intento de abrir la aplicación en el navegador integrado devolvió `The browser access host is unavailable`. Las comprobaciones del usuario simulado no sustituyen la revisión visual de la comparación animada en un navegador real.

Archivos preparados: `pumpcalc/comparacion.py`, `pumpcalc/panel_comparacion.py`, `pumpcalc/ejemplos.py`, `pumpcalc/escena.py`, `pumpcalc/presentacion.py`, `pumpcalc/simulacion.py`, `pumpcalc/vista.py`, `tests/test_comparacion.py`, `tests/test_vista_comparacion.py`, `tests/test_vista.py`, `docs/README.md`, `docs/INSTALACION_LOCAL.md` y `docs/avance.md`. Los cambios ajenos al desarrollo de PumpCalc se conservan fuera del commit.

Commit registrado: `601b3fd` (`feat: comparar escenarios y evaluar el caudal objetivo`). Al retomar el paso 9 se revisaron los 13 archivos preparados antes de registrarlo. La revisión visual pendiente se mantiene documentada.

## Paso 9 Verificar la entrega y preparar la sustentación

Fecha: 11 de noviembre de 2026, America/Bogota.

Estado final: **paso 9 completado**, con instalación limpia, pruebas automatizadas, arranque, documentación y aceptación visual comunicada por el usuario. La limitación de acceso directo del agente al navegador se conserva como parte de la evidencia.

Se creó un entorno independiente en `.tmp\entrega-limpia-20261111` y se instaló `requirements.txt`. Se confirmó Python 3.13.7, NiceGUI 4.0.0, pytest 9.2.0 y aislamiento respecto del intérprete base. `python -m pip check` informó `No broken requirements found.`. Después de añadir comentarios de unidades, dominio, transición y cota numérica, `python -m pytest` produjo **282 passed, 1 skipped in 7.08s**. La omisión corresponde al módulo heredado de interfaz CustomTkinter, que no forma parte de la entrega web.

El arranque con el intérprete nuevo mostró `NiceGUI ready to go on http://127.0.0.1:8080`. La solicitud HTTP devolvió 200 y contenía resultado base, copiar A/B, comparación, objetivo común, ejemplos y pausa. El servidor se detuvo al terminar. El navegador integrado devolvió `The browser access host is unavailable`; no se declara observado el dibujo o movimiento real. El informe deja un recorrido visual concreto para resolver esta verificación pendiente.

Se ejecutaron nuevamente las referencias desde el entorno limpio: Q de A = 3,765449524 m³/h; B = 4,381752014 m³/h; L = 80 m = 3,227949142 m³/h; Δz = 40 m = sin intersección. Los tres puntos cumplen las tolerancias de referencia y las dos condiciones internas de bisección. Se verificaron también el factor laminar, Colebrook de referencia, la raíz analítica y la meta A/B. Las cifras completas y el alcance de las pruebas están en [VALIDACION_FINAL.md](VALIDACION_FINAL.md).

Entregables: [README raíz](../README.md) como entrada al proyecto, [manual ampliado](README.md) con instalación, tres ejemplos, unidades, métodos, tolerancias y tutorial del motor; [guía de sustentación](GUIA_SUSTENTACION.md) de 6–8 minutos; [informe de verificación](VALIDACION_FINAL.md) con evidencia y pendientes. Se actualizó [instalación local](INSTALACION_LOCAL.md) y se comentaron cuatro módulos del motor sin cambiar sus algoritmos. Se conservaron intactas las fuentes de verdad y los antecedentes de escritorio.

Se verificaron los enlaces locales y los bloques Markdown de los seis documentos afectados. El tutorial del manual se ejecutó en el entorno limpio y reprodujo el caso base. Se confirmó que el servidor de comprobación quedó detenido y se revisó el diff preparado sin errores de espacios.

Archivos preparados: `README.md`, `docs/README.md`, `docs/INSTALACION_LOCAL.md`, `docs/GUIA_SUSTENTACION.md`, `docs/VALIDACION_FINAL.md`, `docs/avance.md`, `pumpcalc/comparacion.py`, `pumpcalc/entradas.py`, `pumpcalc/friccion.py` y `pumpcalc/operacion.py`.

Commit registrado: `89431fd` (`chore: verificar y documentar la entrega de PumpCalc`). Al retomar se confirmó que contenía los 10 archivos preparados y que el árbol de trabajo estaba limpio; no se duplicó.

### Cierre de la aceptación manual

Fecha: 11 de noviembre de 2026, America/Bogota.

Se volvió a intentar el navegador integrado, que devolvió `The browser access host is unavailable`. Se dejó la aplicación ejecutándose para revisión local y se comprobó HTTP 200 con resultado base, comparación y pausa. Se pidió al usuario revisar A/B con D = 32 mm, mayor caudal y trazas más lentas, pausa/reanudación, entrada inválida D = 0 y ejemplo sin intersección. Respondió **«lo veo bien»**. Se registra como aceptación visual general del recorrido solicitado, sin atribuir al agente observación directa ni resultados individuales no informados por el usuario.

Con esta aceptación se cierra el pendiente visual del paso 9 y el plan de nueve pasos queda completado. Se actualizaron los seis documentos de entrega para reflejar el cierre y el commit ya registrado. Este ajuste es documental: no cambia el código ni requiere repetir la suite numérica; conserva el resultado previo de 282 pruebas aprobadas y una omisión heredada.

Commit de cierre documental propuesto: `docs: registrar la aceptación visual de PumpCalc`. Se deja preparado para registrar al decir «sigamos»; ese turno cierra Git sin iniciar otro paso de desarrollo.
