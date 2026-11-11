# PumpCalc necesidad y requerimientos

**Estado documental:** especificación vigente, sincronizada el 10 de noviembre de 2026. Describe la entrega requerida; no certifica que el código existente ya la implemente.

Fuentes de verdad: [propuesta v4](../Baseline%20y%20pasos/PumpCalc%20propuesta%20v4.docx), [línea base con animación](../Baseline%20y%20pasos/PumpCalc_linea_base_Codex_con_animacion.md) y [plan de desarrollo por pasos](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md). La propuesta y la línea base fijan el producto y los cálculos; el plan establece el orden de implementación y verificación. Los documentos de `docs` desarrollan esas fuentes y no las sustituyen.

## Necesidad y público

El público inicial son estudiantes y docentes que quieren experimentar y explicar cómo una instalación modifica el caudal de una bomba. La pregunta principal es qué caudal entregaría esta bomba en esta instalación según el modelo y qué cambia al modificar una condición. El uso posterior por instaladores, vendedores o clientes es una posibilidad de demostración y aprendizaje; no hay demanda comercial validada ni una certificación de instalaciones.

Cada escenario contiene una instalación con un único desnivel y una curva de bomba. A y B son configuraciones independientes. Sus niveles permanecen fijos durante cada cálculo; no representan obligatoriamente un tanque casi vacío y casi lleno. La meta es opcional y común a ambos escenarios.
## Alcance de la entrega final

### Instalación que se representará

Se modelará una bomba centrífuga a velocidad fija que transporta agua entre dos depósitos abiertos a la atmósfera, mediante una única línea de tubería circular de diámetro interno y rugosidad constantes. La longitud será la suma de las longitudes físicas de la línea, sin añadir longitudes equivalentes por accesorios, cuyas pérdidas se representarán mediante un coeficiente total K.

Los niveles de los depósitos se considerarán fijos durante cada cálculo. Se supondrá tubería llena, flujo unidireccional y estacionario, agua incompresible y velocidades despreciables en las superficies de los depósitos. El desnivel será la diferencia entre esas superficies, no la altura física de ubicación de la bomba. Se admitirán destinos al mismo nivel o más altos que el origen.

### Funcionalidades obligatorias

- **Configurar una instalación.** Introducir longitud, diámetro interno, desnivel, rugosidad y K total. K será un campo agregado; no se construirá un catálogo de accesorios.
- **Definir una bomba.** Introducir entre 3 y 10 pares de caudal y altura. Habrá una curva ficticia precargada para comenzar sin buscar fichas técnicas.
- **Simular.** Calcular el punto de operación, la velocidad, las pérdidas y el régimen de flujo, o explicar por qué no se obtuvo una solución dentro de los datos disponibles.
- **Animar el agua.** Mostrar su movimiento continuo por la tubería en una escena 2D. La rapidez visual cambiará con la velocidad calculada al modificar los parámetros y podrá pausarse.
- **Comparar A y B.** Conservar dos configuraciones independientes en memoria, copiar A en B y modificar cualquier entrada de B. Mostrar la diferencia de caudal y las condiciones de cada caso.
- **Evaluar una meta.** Admitir un caudal objetivo opcional y común para A y B. Informar si cada escenario lo alcanza dentro del modelo y mostrar el margen de caudal.
- **Explicar el cálculo.** Mostrar las curvas, etiquetas sobre la escena animada y un panel desplegable con métodos, tolerancias e iteraciones.

Se incluirán tres ejemplos listos para cargar en el escenario activo: caso base, cambio de diámetro y caso sin intersección. El caso base se calculará y animará al iniciar. Las configuraciones durarán mientras permanezca abierta la aplicación; recargar restaurará el ejemplo inicial.

### Límites que protegen la viabilidad

La entrega no incluirá redes ramificadas, varios tramos con diámetros distintos, bombas en serie o paralelo, velocidad variable de la bomba, selección automática de equipos, optimización ni catálogos comerciales. Tampoco incluirá evolución temporal del nivel de los tanques, tiempo de llenado, control automático, sensores, cavitación, NPSH, golpe de ariete, aire, sólidos o temperatura variable.

No se calcularán eficiencia, consumo eléctrico, costos ni ahorro económico. No habrá cuentas, base de datos, servicios de IA, importación de archivos, exportación de informes ni publicación obligatoria en internet. La aplicación se ejecutará con el servidor local incluido en NiceGUI.

La aplicación identificará sus resultados como estimaciones de un modelo educativo. Alcanzar el caudal objetivo no certificará la idoneidad de una instalación real: el modelo no evalúa todos los fenómenos necesarios para esa conclusión.


## Experiencia de uso y resultados

### Recorrido principal

1. El usuario abre el caso base, ve el agua moverse y revisa los datos de instalación y bomba.
2. Cambia un parámetro y observa la actualización del movimiento, los indicadores y las curvas. **Simular** permite recalcular inmediatamente.
3. Copia A en B, cambia una condición y simula B. Puede cambiar varias, aunque los ejemplos modificarán solo una para facilitar la interpretación.
4. Compara las animaciones y los resultados de A y B, y consulta el detalle numérico para explicar o verificar el cálculo.

### Una vista principal

La interfaz estará en español y priorizará su uso en computador. Tendrá un formulario de instalación, una tabla editable de la curva de la bomba y una zona de resultados. A y B se seleccionarán mediante pestañas o controles equivalentes; no se crearán páginas independientes para cada función.

La escena central mostrará depósitos, bomba y tubería con agua en movimiento, con etiquetas de longitud, diámetro y desnivel. La animación será parte obligatoria del producto, como se precisa en la sección 4. La gráfica usará caudal en m³/h y altura en metros, con leyenda y marcadores identificados.

### Resultados que se mostrarán

Para una solución válida se presentarán **caudal de operación Q**, **altura de operación H**, velocidad del agua, pérdidas en tubería y accesorios, número de Reynolds, factor de fricción de Darcy y régimen de flujo. La altura H será la energía por unidad de peso suministrada por la bomba, expresada en metros; no se presentará como una presión medida en un punto de la tubería.

La gráfica mostrará los puntos ingresados de la bomba, su interpolación, la curva del sistema y el cruce calculado. En la comparación se superpondrán los casos A y B, con una tabla breve de sus entradas y resultados. Cada curva se dibujará solo en su propio intervalo de datos. Se mostrarán la diferencia absoluta de caudal y su porcentaje respecto de A. Si el caudal de A es cero, el porcentaje se indicará como no aplicable.

El objetivo será una referencia, no una restricción que altere la solución. Se mostrará el margen Q menos el caudal objetivo. Si su magnitud no supera la cota de error numérico del caudal, el estado será **En el límite numérico**. En otro caso será **Alcanza la meta en el modelo** o **No alcanza la meta en el modelo**.

### Estados y mensajes

Se distinguirán datos inválidos, cálculo pendiente, solución encontrada, ausencia de intersección y falta de convergencia. Editar una entrada del modelo invalidará su resultado y suspenderá el movimiento hasta completar el recálculo automático. Una comparación no presentará resultados desactualizados como vigentes.

Si falta un cruce, se conservarán las curvas y se explicará su posición relativa en el intervalo disponible. No se inventará un caudal ni se extrapolará la curva. Si falla el cálculo de fricción, se propagará ese fallo y no se presentará una solución aparente. Los mensajes se ubicarán junto al campo o resultado pertinente.


## Entradas y modelo hidráulico

### Datos admitidos

Los límites siguientes delimitan el sandbox; no son límites de diseño de equipos reales. Todos los campos deberán ser finitos. La interfaz aceptará coma o punto decimal, sin separadores de miles.

| Dato | Unidad visible | Dominio admitido |
| --- | --- | --- |
| Longitud total L | m | Mayor que 0 y hasta 1000 y L ≥ Δz |
| Diámetro interno D | mm | De 10 a 200 |
| Desnivel Δz | m | De 0 a 100 |
| Rugosidad absoluta ε | mm | De 0 a 1 y además ε/D ≤ 0,05 |
| Coeficiente total K | Sin unidad | De 0 a 100 |
| Caudal de cada punto | m³/h | De 0 a 100 |
| Altura de cada punto | m | De 0 a 200 |
| Caudal objetivo opcional | m³/h | Mayor que 0 y hasta 100 |

La curva tendrá de 3 a 10 puntos con caudales estrictamente crecientes, alturas no crecientes y un intervalo de caudal de amplitud positiva. Se rechazarán duplicados, desorden y alturas crecientes, sin corregirlos silenciosamente. No será obligatorio que el primer caudal sea cero.

Se fijarán g = 9,81 m/s² y viscosidad cinemática ν = 1,004 × 10⁻⁶ m²/s como aproximación al agua a 20 °C. No se necesitará densidad porque se trabajará en alturas de energía. La rugosidad se introducirá directamente; el ejemplo usará un valor aproximado de tubería plástica lisa [3].

### Ecuaciones del sistema

Todo el cálculo interno usará metros, segundos y m³/s. Se convertirá el caudal visible dividiendo entre 3600 y las entradas en milímetros dividiendo entre 1000. Para Q mayor que cero [3, 5]:

$$
A = \frac{\pi D^2}{4}, \qquad v = \frac{Q}{A}, \qquad Re = \frac{vD}{\nu}
$$

$$
h_f = f\frac{L}{D}\frac{v^2}{2g}, \qquad h_K = K\frac{v^2}{2g}
$$

$$
H_s(Q) = \Delta z + h_f(Q) + h_K(Q)
$$

K representará la suma de pérdidas localizadas, incluidas entrada y descarga cuando correspondan. El caso precargado usará K = 4 como dato didáctico agregado. La aplicación no añadirá coeficientes ocultos ni otro término de velocidad a la ecuación entre superficies de los depósitos.

En Q = 0 se establecerán v = 0, Re = 0, pérdidas iguales a cero y Hs = Δz, sin evaluar 64/Re ni Colebrook. El factor de fricción se mostrará como no aplicable. Se usará siempre el factor de Darcy, no el de Fanning.


## Requisitos verificables

Los identificadores siguientes corresponden a esta revisión y sustituyen el catálogo anterior. No son un inventario de funcionalidades ya implementadas. Todos son parte de la entrega requerida.

| ID | Requisito | Criterio de aceptación | Plan |
| --- | --- | --- | --- |
| RF-01 | Capturar L, D, Δz, ε y K total. | Cumple los dominios anteriores, acepta coma o punto, distingue vacío de cero y rechaza valores no finitos. | 2 y 5 |
| RF-02 | Editar entre 3 y 10 puntos de bomba. | Caudales estrictamente crecientes, alturas no crecientes, sin ordenar ni corregir silenciosamente; sin extrapolación. | 2 |
| RF-03 | Calcular el punto con los tres métodos propios. | Interpolación lineal, punto fijo para Colebrook y bisección con las tolerancias de la línea base. | 2 a 4 |
| RF-04 | Recalcular y conservar la coherencia del resultado. | Editar invalida el resultado; recálculo tras 200 ms sin cambios válidos; Simular actúa inmediatamente. | 5 |
| RF-05 | Mostrar indicadores, curvas y trazas numéricas. | Q, H, v, pérdidas, Re, f y régimen; 150 muestras por escenario y marcador calculado por el motor. | 6 |
| RF-06 | Animar el agua según v. | Escala común s(v) = 240v/(v+2), diámetro visible, pausa y suspensión en estados sin resultado vigente. | 7 |
| RF-07 | Comparar A y B independientes en memoria. | Copiar A en B no comparte datos mutables; editar B no modifica A; recargar restaura el ejemplo inicial. | 8 |
| RF-08 | Evaluar una meta opcional común. | Muestra margen Q − objetivo y los tres estados definidos; cambiar solo la meta no cambia el punto de operación. | 8 |
| RF-09 | Cargar tres ejemplos en el escenario activo. | Base, diámetro de 32 mm y ausencia de intersección; el caso base se calcula y anima al iniciar. | 8 |
| RF-10 | Distinguir errores y ausencia de solución. | Datos inválidos, pendiente, solución, sin cruce y falta de convergencia; nunca asignar cero a una solución inexistente. | 4 a 8 |

| ID | Requisito no funcional | Evidencia requerida |
| --- | --- | --- |
| RNF-01 | Todo el código del proyecto en Python, motor independiente de NiceGUI. | Cálculo verificable sin interfaz; métodos explícitos, sin bibliotecas que los resuelvan por detrás. |
| RNF-02 | Web local NiceGUI en español, orientada a computador. | Una vista principal; servidor en 127.0.0.1 y arranque con `python app.py`. |
| RNF-03 | Unidades y precisión consistentes. | Motor en m, s y m³/s; presentación en mm, m y m³/h según el campo; redondeo solo al mostrar. |
| RNF-04 | Trazabilidad y sincronización. | Escena, indicadores y curvas usan el mismo resultado vigente de cada escenario. |
| RNF-05 | Instalación reproducible y comprobada. | Versiones verificadas de NiceGUI y pytest fijadas, versión de Python documentada y entorno limpio probado. |
| RNF-06 | Resultados educativos con límites explícitos. | Datos ficticios identificados, movimiento ilustrativo y meta sin certificar una instalación real. |

## Historias de usuario y aceptación

| Historia | Aceptación observable |
| --- | --- |
| Como estudiante, quiero comenzar con un ejemplo para explorar la instalación. | Al abrir se calcula y anima A con la curva ficticia y los datos base. |
| Como estudiante, quiero cambiar una entrada para entender su efecto. | El resultado se invalida y se actualizan juntos cifras, curvas y movimiento al recalcular. |
| Como estudiante, quiero comparar una alternativa sin perder la original. | Copio A en B, cambio D de 25 a 32 mm y observo mayor Q y menor v, con A intacto. |
| Como usuario, quiero contrastar una meta con ambos resultados. | Con objetivo de 4 m³/h, A no lo alcanza y B sí; si el margen cae dentro de la cota numérica se informa En el límite numérico. |
| Como docente, quiero examinar el cálculo. | Puedo consultar tramo interpolado, régimen, tolerancias, residuo, tabla de bisección y la traza de fricción del resultado final. |
| Como usuario, quiero entender por qué no hay resultado. | La aplicación distingue entradas inválidas, ausencia de cruce y falta de convergencia; suspende el movimiento y evita cifras inventadas. |

Las ecuaciones y referencias numeradas se explican en [Documento del proyecto](DOCUMENTO_PROYECTO.md). Los valores esperados y las pruebas obligatorias están en [Caso de finca y validación](CASO_FINCA_Y_VALIDACION.md). Las referencias a secciones dentro del contenido de la línea base conservan la numeración de esa fuente.
