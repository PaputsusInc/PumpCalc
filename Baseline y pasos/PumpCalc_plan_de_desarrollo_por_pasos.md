# PumpCalc Plan de desarrollo en Python

Usa este plan junto con **PumpCalc_linea_base_Codex_con_animacion.md**. La propuesta define el alcance y los cálculos. Escribe todo el código del proyecto en Python. Usa NiceGUI para la interfaz web local, las gráficas y la animación, y `pytest` para las pruebas. El plan define el orden de trabajo y los commits.

**En el primer turno, lee los dos archivos y ejecuta solo el paso 1.** Trabaja en la carpeta local de PumpCalc. Si el proyecto ya tiene avances, revísalos antes de editar y retoma el primer paso pendiente. Si no tienes acceso a los archivos, al terminal o al repositorio, dilo: no reportes cambios, pruebas ni commits simulados.

## Ritmo de trabajo y commits

1. **Haz un paso por turno.** Implementa solo lo necesario para ese paso, junto con sus pruebas. Respeta la propuesta: una bomba, una tubería, animación 2D y dos escenarios. Mantén los cálculos separados de la interfaz.
2. **Verifica antes de preparar el commit.** Ejecuta las comprobaciones del paso. Desde el paso 2, ejecuta `python -m pytest` en el entorno virtual. Cuando cambie la interfaz, inicia `python app.py` y comprueba el comportamiento nuevo en el navegador. Si falla una comprobación esencial, corrígela o informa lo que falta para completar el paso.
3. **Deja listo el commit y detente.** Prepara en Git únicamente los cambios del paso y revisa lo que se registraría con `git diff --cached`. «Commit preparado» significa que los cambios están listos para registrar, pero que **todavía no se ha creado el commit**. Conserva el trabajo previo del usuario; no lo incluyas en el commit por accidente. Anota brevemente en `docs/avance.md` el paso y sus comprobaciones reales, para poder retomar en otra sesión.
4. **Cuando yo diga «sigamos»**, revisa que los cambios preparados sigan siendo los que me mostraste, crea ese commit local y continúa únicamente con el paso siguiente. Si el contenido preparado cambió, o si el commit falla, informa y detente antes de avanzar. Si el paso actual no estaba listo, retómalo primero. Si ya se verificó sin cambios o su commit ya quedó registrado, continúa sin duplicarlo. Al terminar el último paso, «sigamos» registra el último commit pendiente y cierra la entrega.

Si digo **«ajusta…»**, corrige el paso actual, verifica y vuelve a preparar su commit. Si digo **«haz el commit»**, regístralo y espera sin empezar otro paso. Si un paso ya estaba implementado, verifícalo y dilo; no hagas un commit vacío. Los commits son locales: no hagas push, despliegues ni crees PR sin que lo pida.

### Respuesta al cerrar cada paso

Usa este formato cuando el paso esté verificado y preparado. Completa los campos con hechos observados:

```text
Paso N completado. Commit preparado.
Resultado: [qué quedó funcionando y cómo puedo verlo].
Verificación: [pruebas o comprobaciones ejecutadas y su resultado].
Commit propuesto: [mensaje del commit].
Siguiente: [paso que se ejecutará al decir «sigamos»].
```

Si registraste un commit al comenzar el turno, indica también su identificador corto. Si el paso está incompleto, indica el estado real, el problema y qué falta. No anuncies como ejecutada una verificación que solo sugeriste.

## Paso 1 Preparar el proyecto local

- Comprueba que trabajas en la carpeta de PumpCalc y revisa su estado en Git. Si es una carpeta nueva destinada al proyecto, inicializa Git allí; si ya hay un repositorio, conserva su estructura y el trabajo existente.
- Crea el entorno con `python -m venv .venv`. Fija las versiones verificadas de NiceGUI y `pytest` en `requirements.txt` e instala las dependencias con `python -m pip install -r requirements.txt` desde el entorno. Documenta la versión de Python y los comandos. Excluye `.venv`, `__pycache__` y `.pytest_cache` del control de versiones.
- Crea `app.py` con una vista inicial de PumpCalc. Configura NiceGUI para escuchar en `127.0.0.1`. Organiza el código en módulos de Python para cálculo, interfaz y ejemplos a medida que se incorporen.

**El paso queda listo** cuando `python app.py` inicia la aplicación y la vista inicial de PumpCalc se abre en el navegador. Las pruebas numéricas empiezan en el paso 2.

**Commit sugerido:** `chore: preparar la base local de PumpCalc`

## Paso 2 Validar entradas e interpolar la bomba

- Define los datos del escenario y de la curva. Aplica los límites de la sección 5 de la propuesta. Admite coma o punto decimal, distingue vacío de cero y convierte las unidades al ingresar al motor: mm a m y m³/h a m³/s.
- Implementa la interpolación lineal por tramos con funciones de Python independientes de NiceGUI. Rechaza datos de curva duplicados o desordenados y alturas crecientes. Limita la evaluación al intervalo de la curva, incluidos sus extremos.
- Guarda la curva ficticia y la instalación base como datos de ejemplo reutilizables. Los valores esperados de las pruebas se toman de la propuesta, no de la salida del motor que se está probando.

**Listo cuando:** las pruebas reproducen los nodos, dan 28,5 m a 2,5 m³/h, rechazan extrapolar y comprueban conversiones y entradas inválidas representativas.

**Commit sugerido:** `feat: validar entradas e interpolar la curva de la bomba`

## Paso 3 Calcular las pérdidas hidráulicas

- Implementa área, velocidad, Reynolds, factor de fricción de Darcy, pérdidas en tubería y accesorios y altura del sistema. Usa las constantes y las unidades de la propuesta.
- Implementa Colebrook por punto fijo con sus controles de convergencia. Aplica las reglas del modelo para flujo laminar y transición. Trata Q = 0 aparte y devuelve información del régimen, pérdidas e iteraciones cuando corresponda.

**Listo cuando:** las pruebas verifican caudal cero sin división por cero, f = 0,064 para Re = 1000, el valor turbulento de referencia de la sección 9, continuidad en los dos límites de transición y manejo explícito de la falta de convergencia.

**Commit sugerido:** `feat: calcular fricción y pérdidas hidráulicas`

## Paso 4 Resolver y verificar el punto de operación

- Implementa bisección sobre la diferencia de alturas en el intervalo de la bomba. Usa las dos tolerancias y el límite de iteraciones de la sección 7. Distingue raíz en el extremo, cruce, ausencia de cruce y falta de convergencia.
- Devuelve Q, H, v, pérdidas, régimen, residuo y traza. Calcula el cruce con el modelo; las muestras de la gráfica se añadirán después.
- Verifica la raíz analítica de la sección 9 y los casos hidráulicos de la sección 8: base, cambio a D = 32 mm, cambio a L = 80 m y desnivel sin intersección. Incluye extremos, nodo interior, dominio que empieza por encima de cero y ambos casos sin cambio de signo.

**Listo cuando:** el motor reproduce, dentro de las tolerancias de la propuesta, Q ≈ 3,765443 m³/h en A y Q ≈ 4,381758 m³/h en B, además de las demás referencias. No hay caudal inventado en casos sin solución.

**Commit sugerido:** `feat: resolver el punto de operación por bisección`

## Paso 5 Conectar el formulario y los resultados

- Construye en Python una sola vista de NiceGUI en español para editar las entradas y la tabla de la bomba. Carga el caso base y muestra los indicadores de un escenario usando el motor verificado.
- Invalida el resultado al editar datos del modelo. Con entradas válidas, recalcula tras 200 ms sin cambios; **Simular** recalcula de inmediato. Presenta los estados de la propuesta con mensajes y unidades claros.

**Listo cuando:** en el navegador se puede cargar A, editarlo y obtener resultados nuevos; un dato inválido se señala y no deja el resultado anterior como vigente. Todavía se trabaja con un escenario visible.

**Commit sugerido:** `feat: conectar entradas y simulación de un escenario`

## Paso 6 Dibujar las curvas y explicar el cálculo

- Configura `ui.echart` desde Python con dos ejes numéricos y sus unidades. Muestra los puntos de la bomba, su curva interpolada y la curva del sistema con las 150 muestras de la propuesta. Marca el cruce que devolvió el motor cuando exista. Si las curvas no se cruzan, muestra las curvas y el aviso correspondiente.
- Añade el detalle desplegable de bisección con iteraciones, intervalos, tolerancias y residuo. Muestra el tramo interpolado y el cálculo de fricción pertinente, distinguiendo flujo laminar, transición y turbulencia.

**Listo cuando:** el marcador y los indicadores coinciden con el resultado calculado, se puede seguir la convergencia y las curvas no se extienden fuera del dominio de la bomba.

**Commit sugerido:** `feat: mostrar las curvas y el detalle numérico`

## Paso 7 Animar el agua en la instalación

- Genera desde Python la escena 2D con depósitos, bomba, tubería y trazas de agua que se muevan de origen a destino. Usa `ui.interactive_image` con una capa para la instalación y otra para las trazas. El grosor visual de la tubería responderá al diámetro.
- Usa `ui.timer` para mover la capa de trazas según el tiempo transcurrido y **v, la velocidad calculada del agua**, con la escala de la sección 4. El temporizador utiliza el resultado vigente del motor. El formulario activa los recálculos.
- Permite pausar y reanudar la animación. Suspende el movimiento mientras el resultado esté pendiente, sea inválido o no exista; muestra el estado correspondiente. En una solución válida con Q = 0, no hay movimiento.

**Listo cuando:** el caso base se ve en movimiento. Al cambiar D de 25 a 32 mm, la tubería se ve más ancha y el agua avanza más despacio (v pasa de ≈ 2,131 a ≈ 1,513 m/s), aunque el caudal sube. Pausar no cambia los resultados y, si no hay cruce, la escena queda sin movimiento con su aviso.

**Commit sugerido:** `feat: animar el flujo de agua según la velocidad calculada`

## Paso 8 Comparar escenarios y probar una meta

- Implementa A y B como escenarios independientes en memoria. Permite copiar A en B y cargar cualquiera de los tres ejemplos de la propuesta en el escenario activo. Al recargar la página se restablece el caso base.
- Compara las dos animaciones con una escala común, sus curvas e indicadores. Muestra el cambio de caudal y el porcentaje respecto de A cuando sea aplicable. En cada caso, conserva su dominio y distingue resultados vigentes de los pendientes o sin solución.
- Añade el caudal objetivo opcional y común a A y B. Evalúa margen y estado según la propuesta, sin cambiar el punto de operación.

**Listo cuando:** el usuario copia A, cambia solo B y ve ambos casos. A permanece intacto. Con la meta de 4 m³/h, A queda por debajo y B la supera; con el ejemplo sin intersección se muestra el aviso sin inventar un valor de comparación.

**Commit sugerido:** `feat: comparar escenarios y evaluar el caudal objetivo`

## Paso 9 Verificar la entrega y preparar la sustentación

- Crea un entorno virtual limpio e instala `requirements.txt` con `python -m pip install -r requirements.txt`. Ejecuta `python -m pytest`, inicia `python app.py` y recorre la aplicación en el navegador. Demuestra el caso base, el cambio de diámetro, el caso sin intersección, una entrada inválida y la pausa de la animación.
- Completa el README con la versión de Python, la instalación, el arranque, las pruebas y los tres ejemplos. Explica cómo se conectan interpolación, punto fijo y bisección, cuáles son sus tolerancias y qué significan los resultados. Registra las comprobaciones y sus valores observados.
- Deja una guía breve de sustentación: mostrar A, duplicarlo en B, cambiar el diámetro, explicar por qué sube el caudal y baja la velocidad, mostrar las iteraciones y terminar con el caso sin cruce.
- Comenta las partes del código que necesitan una explicación, como unidades, condiciones de parada y tratamiento de casos límite. Si se usa la skill recomendada, aplícala en este paso para explicar los módulos del motor en Python y preparar el tutorial del README. Repite las pruebas después de editar el código. [Skill para comentar código y generar un tutorial](https://github.com/github/awesome-copilot/blob/main/skills/comment-code-generate-a-tutorial/SKILL.md)

**Listo cuando:** se puede instalar y demostrar el proyecto siguiendo el README, las pruebas pasan y están presentes las funciones y límites de la propuesta. Deja listo el último commit y espera «sigamos» para registrarlo.

**Commit sugerido:** `chore: verificar y documentar la entrega de PumpCalc`
