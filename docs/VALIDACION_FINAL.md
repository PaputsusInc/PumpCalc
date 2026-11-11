# Informe de verificación de entrega

Fecha: **11 de noviembre de 2026**, America/Bogota. Base de código: commit `89431fd` del paso 9, que incorpora la implementación del paso 8 (`601b3fd`). Este cierre documental registra la aceptación manual posterior. Referencias: secciones 8–10 de la [línea base](../Baseline%20y%20pasos/PumpCalc_linea_base_Codex_con_animacion.md) y [plan por pasos](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md).

**Estado:** paso 9 completado con instalación limpia, pruebas automatizadas, arranque HTTP y aceptación visual comunicada por el usuario. La revisión manual se apoya en su confirmación general del recorrido, con el alcance descrito abajo.

## Instalación y ejecución observadas

Se creó un entorno nuevo en `.tmp\entrega-limpia-20261111`, sin reutilizar `.venv`, y se instalaron las dependencias de `requirements.txt` mediante pip. El intérprete confirmó aislamiento respecto del Python base. El entorno y los registros temporales no se versionan.

| Comprobación | Resultado observado |
| --- | --- |
| Python | 3.13.7 en Windows |
| NiceGUI / pytest | 4.0.0 / 9.2.0 |
| `python -m pip install -r requirements.txt` | Instalación finalizada correctamente en el entorno nuevo |
| `python -m pip check` | `No broken requirements found.` |
| `python -m pytest` | **282 passed, 1 skipped in 7.08s** |
| `python app.py` | `NiceGUI ready to go on http://127.0.0.1:8080` |
| Solicitud HTTP a `/` | Estado **200**; resultado base, copiar A en B, comparar A/B, objetivo común, cargar ejemplo y pausa presentes en la respuesta |
| Navegador integrado | `The browser access host is unavailable` |

Los comandos se ejecutaron con `.\.tmp\entrega-limpia-20261111\Scripts\python.exe`. El resultado de pytest quedó en `.tmp\verificacion-final-pytest.txt`. Las pruebas se ejecutaron después de añadir los comentarios del paso 9: no hubo cambios de algoritmo. El servidor de comprobación se detuvo al terminar.

Se comprobaron los enlaces locales y el cierre de bloques Markdown de los seis documentos de entrega modificados o añadidos. El tutorial Python del manual se extrajo y ejecutó correctamente en el entorno limpio, con el mismo Q, H, v y residuo del caso A.

El módulo omitido corresponde a la interfaz de escritorio heredada que depende de CustomTkinter, ausente de `requirements.txt`. Las pruebas NiceGUI sí se ejecutaron. El código web usa `app.py`; `main.py` y sus dependencias se conservan como antecedentes.

## Contraste numérico con las fuentes

Los valores de referencia provienen de la línea base, no de resultados generados por las pruebas. La ejecución independiente del motor en el entorno limpio produjo:

| Caso | Q referencia (m³/h) | Q observado (m³/h) | H referencia (m) | H observada (m) |
| --- | --- | --- | --- | --- |
| A: D = 25 mm | 3,765443 | 3,765449524 | 20,641896 | 20,641853333 |
| B: D = 32 mm | 4,381758 | 4,381752014 | 15,564175 | 15,564231873 |
| Solo L = 80 m | 3,227947 | 3,227949142 | 24,404369 | 24,404356003 |
| Solo Δz = 40 m | Sin intersección | Sin intersección | No aplica | No aplica |

En los tres puntos calculados, el error absoluto es menor que **0,001 m³/h** para Q y **0,001 m** para H. El caso sin cruce devuelve punto ausente, sin inventar un caudal cero.

| Caso | Iteraciones de bisección | Residuo F(Q) (m) | Cota de Q (m³/s) |
| --- | --- | --- | --- |
| A | 17 | −6,748895978 × 10⁻⁵ | 1,059638129 × 10⁻⁸ |
| B | 17 | +6,666673630 × 10⁻⁵ | 1,059638129 × 10⁻⁸ |
| L = 80 m | 19 | −2,651001611 × 10⁻⁵ | 2,649095323 × 10⁻⁹ |

Los tres satisfacen simultáneamente semiancho ≤ 10⁻⁷ m³/s y residuo absoluto ≤ 10⁻⁴ m. El factor de Darcy de A fue **0,0208399779706244**, dentro del error máximo de 10⁻⁷ respecto de 0,020839985.

Con meta de 4 m³/h, A tuvo margen **−0,234550476 m³/h**, estado **No alcanza la meta en el modelo**; B tuvo **+0,381752014 m³/h**, estado **Alcanza la meta en el modelo**. B − A fue **+0,616302490 m³/h**, **+16,367301867 %** respecto de A. Las velocidades observadas fueron **2,130808550 m/s** en A y **1,513406017 m/s** en B.

## Controles independientes y cobertura

| Control | Resultado |
| --- | --- |
| Interpolación de ejemplo | Los nodos se reproducen y Hb(2,5 m³/h) = 28,5 m; extrapolar se rechaza |
| Laminar, Re = 1000 | f = 0,064 |
| Colebrook, Re = 100000 y ε/D = 0,0001 | f = 0,018513866077451757; error menor que 10⁻⁹ frente a la referencia |
| Raíz aislada de 20 − 2q − q² | Calculada 3,5825756192207336; exacta √21 − 1 ≈ 3,58257569495584 |
| Error y parada de esa raíz | Error 7,573510619 × 10⁻⁸; residuo 6,941237096 × 10⁻⁷; cota 2,980232239 × 10⁻⁷ |

En el control aislado, q está en m³/h y ambas tolerancias son 10⁻⁶ en las unidades de la función. En el motor hidráulico los caudales y tolerancias usan SI.

La suite también cubre conversiones, límites de entrada, vacío frente a cero, duplicados y desorden de curva, continuidad en Re = 2000 y 4000, tratamiento Q = 0 sin fricción, fallos forzados de Colebrook y bisección, raíces en extremos y nodos y dominio con caudal inicial positivo. Comprueba segmentos y 150 muestras de curvas, marcador procedente del solver y trazas numéricas del resultado final.

Los recorridos del **simulador oficial de usuario de NiceGUI** comprobaron recálculo tras 200 ms, Simular inmediato, edición y errores por campo/celda, agregar/quitar filas, copiar y editar B conservando A, cambio de activo durante un cálculo pendiente, ejemplos solo en el activo, comparación, meta sin reconstruir curvas, pausa independiente y recarga de página. No son pruebas con un navegador ni observaciones del aspecto visual.

Las pruebas de animación comprobaron s(0) = 0, crecimiento con v, grosor creciente con D, recorrido de trazas, avance según el tiempo, pausa y suspensión sin resultado vigente. Las comprobaciones de componentes verificaron que los fotogramas actualizan la capa de trazas sin recalcular el motor o reconstruir las curvas.

## Aceptación visual comunicada por el usuario

El 11 de noviembre de 2026 se dejó la aplicación ejecutándose en `http://127.0.0.1:8080`, se comprobó nuevamente HTTP 200 y se indicó al usuario este recorrido: copiar A en B y cambiar D a 32 mm, comparar mayor caudal y trazas más lentas, probar pausa/reanudación y D = 0, y cargar **Sin intersección** para revisar aviso y escena detenida. Su respuesta fue **«lo veo bien»**. Se registra como aceptación visual general del recorrido solicitado y permite cerrar el pendiente del paso 9.

El acceso del agente al navegador integrado siguió devolviendo `The browser access host is unavailable`. El agente no observó directamente el dibujo ni el movimiento. El usuario no identificó navegador o versión ni aportó resultados individuales de cada acción; no se atribuyen mediciones o comprobaciones pormenorizadas a su respuesta. La evidencia automatizada se conserva separada de esta aceptación manual.

### Guion para repetir la revisión

1. Abrir la aplicación y observar caso base, unidades, curvas, marcador y trazas en movimiento.
2. Copiar A en B, cambiar D a 32 mm y comparar ambas escenas: A intacto, B más ancho, trazas más lentas y cifras coherentes.
3. Mostrar las iteraciones y comprobar legibilidad de tablas y tolerancias.
4. Pausar y reanudar cada escena, conservando los resultados.
5. Introducir D = 0, revisar error y suspensión del movimiento; restaurar 32 mm y comprobar recuperación.
6. Cambiar solo la meta, conservando el punto de operación y actualizando margen y estado.
7. Cargar **Sin intersección** en B y observar aviso, ausencia de marcador de B y escena detenida.
8. Recargar y recuperar ambos casos base y la meta de demostración.

Este guion sirve para futuras revisiones y no es un registro de observaciones individuales realizadas por el agente. La [guía de sustentación](GUIA_SUSTENTACION.md) propone el recorrido de exposición.

## Límites de la evidencia

Las tolerancias certifican consistencia numérica con las referencias del modelo propuesto. No cuantifican errores de medición, variaciones de bombas reales ni incertidumbre física. La transición es una aproximación didáctica advertida. La animación representa flujo en una tubería llena con niveles fijos, sin escala geométrica ni llenado temporal. No se ha realizado una validación experimental de una instalación física.
