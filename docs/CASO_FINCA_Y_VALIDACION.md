# PumpCalc casos de demostración y validación

**Estado documental:** especificación vigente, sincronizada el 10 de noviembre de 2026. Describe la entrega requerida; no certifica que el código existente ya la implemente.

Fuentes de verdad: [propuesta v4](../Baseline%20y%20pasos/PumpCalc%20propuesta%20v4.docx), [línea base con animación](../Baseline%20y%20pasos/PumpCalc_linea_base_Codex_con_animacion.md) y [plan de desarrollo por pasos](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md). La propuesta y la línea base fijan el producto y los cálculos; el plan establece el orden de implementación y verificación. Los documentos de `docs` desarrollan esas fuentes y no las sustituyen.

## Relación con el antiguo caso de finca

Se conserva este nombre de archivo para mantener los enlaces del proyecto. La entrega vigente se valida con casos numéricos reproducibles y revisión del recorrido animado. El usuario inicial es estudiante o docente; una finca real no es un requisito de aceptación.

Cada escenario representa dos depósitos abiertos con niveles fijos, una bomba a velocidad fija y una tubería de diámetro y rugosidad constantes. A y B son configuraciones independientes, cada una con un desnivel. No se exige calcular un tanque casi vacío y casi lleno dentro de cada escenario ni se modela el tiempo de llenado.

Los valores siguientes son referencias de la fuente, no resultados observados al ejecutar el código del repositorio en esta actualización. No hay mediciones de campo aportadas por las fuentes revisadas.
## Casos reproducibles y valores de referencia

### Curva de demostración

Los ejemplos compartirán la siguiente curva ficticia. Sus datos no corresponderán a una marca ni se presentarán como una ficha comercial.

| Caudal en m³/h | Altura en m |
| --- | --- |
| 0 | 35 |
| 1 | 34 |
| 2 | 31 |
| 3 | 26 |
| 4 | 19 |
| 5 | 10 |

### Caso base A

Se usarán L = 40 m, D = 25 mm, Δz = 12 m, ε = 0,0015 mm, K = 4 y caudal objetivo de 4 m³/h. Los parámetros del agua serán los de la sección 5.

El modelo produce aproximadamente Q = **3,765443 m³/h** y H = **20,641896 m**. En ese punto v = 2,130805 m/s, Re = 53057,90 y f = 0,020839985. Las pérdidas son 7,716242 m en la tubería y 0,925654 m en accesorios. Por tanto, 12 + 7,716242 + 0,925654 coincide, dentro del redondeo, con la altura de operación. El caso no alcanza la meta de 4 m³/h.

### Cambios controlados

| Escenario | Cambio respecto del caso base | Q en m³/h | H en m |
| --- | --- | --- | --- |
| A | Ninguno | 3,765443 | 20,641896 |
| B | Solo D pasa a 32 mm | 4,381758 | 15,564175 |
| Verificación adicional | Solo L pasa a 80 m | 3,227947 | 24,404369 |
| Sin intersección | Solo Δz pasa a 40 m | No aplica | No aplica |

En B, el mayor diámetro permite superar la meta de caudal, mientras v baja a 1,513408 m/s: la tubería se verá más ancha y el agua avanzará más despacio que en A. Aumentar la longitud reduce el caudal. Con Δz = 40 m, la mayor altura de la bomba queda por debajo de la altura estática exigida; se mostrará la escena sin animar y con el aviso de ausencia de cruce.

Los números anteriores se recalcularon para esta línea base con aritmética de 50 dígitos y Newton para la ecuación de fricción. Son referencias del modelo propuesto, no mediciones físicas. La implementación deberá coincidir con ellos con error absoluto máximo de 0,001 m³/h en Q y 0,001 m en H, además de cumplir sus criterios internos de convergencia. Para f del caso base se admitirá un error absoluto de 10⁻⁷.

Estos casos servirán para demostrar que una misma bomba puede entregar distintos caudales según la instalación y que el simulador responde a cambios concretos sin añadir funciones de optimización.


## Verificación y condiciones de aceptación

### Pruebas necesarias

La verificación combinará resultados conocidos, propiedades del modelo y revisión del recorrido completo. Las pruebas numéricas se ejecutarán sobre el motor de cálculo, independientemente de la interfaz.

| Prueba | Resultado o propiedad que debe comprobarse |
| --- | --- |
| Interpolación | Reproduce todos los nodos y da 28,5 m en 2,5 m³/h con la curva de demostración; rechaza extrapolar. |
| Raíz conocida | Para F(q) = 20 − 2q − q² en [0, 5], obtiene q = √21 − 1 ≈ 3,582575695. q está en m³/h solo en esta prueba aislada del solver. |
| Fricción | En Re = 1000 da f = 0,064. En Re = 100000 y ε/D = 0,0001 da f ≈ 0,018513866077 con error absoluto ≤ 10⁻⁹; converge en los extremos del dominio turbulento. |
| Continuidad y caudal cero | No divide entre cero en Q = 0 y devuelve Hs = Δz. Comprueba continuidad en Re = 2000 y 4000 y aviso en transición. |
| Referencias completas | Reproduce el caso base y las variaciones de diámetro, longitud y desnivel de la sección 8. |
| Fronteras del dominio | Acepta raíces en ambos extremos y en un nodo interior; maneja una curva cuyo primer caudal es mayor que cero. |
| Errores y estados | Rechaza vacíos, valores no finitos, diámetro cero, L menor que Δz, caudales duplicados, desorden y alturas crecientes. Distingue ambos casos sin cambio de signo y el agotamiento de iteraciones. |
| Aislamiento de escenarios | Editar B no altera A. Editar cualquier caso invalida su resultado. Recargar restaura el ejemplo. El objetivo no cambia el punto calculado. |
| Animación vinculada | s(0) = 0 y s aumenta con v. Se comprueba visualmente el cambio A → B, la pausa, el recálculo y la suspensión del movimiento en estados sin solución. |

Para la prueba de raíz conocida se usará tolerancia de caudal de 10⁻⁶ m³/h y residuo de 10⁻⁶ en las unidades de esa función. Es un control matemático del algoritmo; no reemplaza la prueba hidráulica completa. Las pruebas de falta de convergencia podrán forzar un límite de una iteración en el motor, sin exponer esa opción al usuario.

### Qué contará como una entrega terminada

La aplicación deberá instalarse en un entorno virtual de Python siguiendo el README, iniciar localmente con `python app.py` y superar las pruebas con `python -m pytest`. El usuario deberá completar el recorrido A → B → comparación animada, consultar las iteraciones y obtener mensajes claros frente a datos inválidos o falta de cruce. La animación, la gráfica y los indicadores usarán el mismo resultado vigente, con unidades y dominios correctos.

La sustentación mostrará el caso base, el cambio de diámetro y la ausencia de intersección; después explicará el balance de energía, los tres métodos y una verificación conocida. La innovación se defenderá como la integración de experimentación y explicación numérica para un usuario principiante, sin afirmar que inventa la simulación de bombas. Todos los integrantes deberán poder explicar el flujo general y los límites del modelo, como recomienda la rúbrica [2].


## Interpretación de estados y meta

La búsqueda utiliza exactamente el intervalo de la curva. Si F es negativa en ambos extremos, la bomba queda por debajo del sistema en ese intervalo; si es positiva en ambos, queda por encima. Se aceptan raíces en extremos. Ningún mensaje permite concluir qué sucede fuera del dominio de los datos. Un fallo de Colebrook o el agotamiento de bisección se informa como falta de convergencia, no como ausencia de intersección.

Una solución válida con Q = 0 tiene v = 0, Re = 0, pérdidas nulas, Hs = Δz y factor de fricción no aplicable. Se muestra sin movimiento. La falta de solución no se representa con Q = 0.

Para una meta común opcional se calcula el margen Q − objetivo. Si su magnitud no supera la cota numérica del caudal, se muestra **En el límite numérico**; en otro caso, **Alcanza la meta en el modelo** o **No alcanza la meta en el modelo**. El objetivo no altera el cálculo. La cota de bisección mide localización numérica de la raíz y no incertidumbre física.

## Evidencia que debe registrarse al implementar

En `docs/avance.md`, al ejecutar cada paso del plan, se anotarán únicamente sus comprobaciones reales. Para el cierre se registrarán versión de Python y dependencias fijadas, instalación limpia, resultado de `python -m pytest`, valores observados frente a referencias y comprobación en navegador de A, B, ausencia de cruce, entrada inválida y pausa. Esta sincronización documental no da por ejecutadas esas pruebas ni crea un avance ficticio.

## Uso posterior en una finca

Una eventual contrastación de campo necesitaría identificar la instalación y la curva, medir longitud, diámetro interno, niveles y caudal, y justificar ε y K. Habría que distinguir mediciones, datos de ficha y supuestos antes de contrastar una condición estacionaria con el modelo. No se fijan tolerancias físicas sin evidencia ni se incluye esa campaña en la entrega actual.

El modelo no evalúa cavitación, NPSH, cebado, transitorios, eficiencia, potencia, costos ni todos los factores de idoneidad de una instalación. Alcanzar la meta solo describe el resultado del modelo educativo. La ubicación de la bomba no añade un campo obligatorio ni sustituye el desnivel entre superficies.

Las ecuaciones y las referencias numeradas de la línea base están en [Documento del proyecto](DOCUMENTO_PROYECTO.md). Las menciones a las secciones 5, 8 y 9 conservan la numeración de la fuente original.
