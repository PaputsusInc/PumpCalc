# PumpCalc contexto y modelo numérico

**Estado documental:** especificación vigente, sincronizada el 10 de noviembre de 2026. Describe la entrega requerida; no certifica que el código existente ya la implemente.

Fuentes de verdad: [propuesta v4](../Baseline%20y%20pasos/PumpCalc%20propuesta%20v4.docx), [línea base con animación](../Baseline%20y%20pasos/PumpCalc_linea_base_Codex_con_animacion.md) y [plan de desarrollo por pasos](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md). La propuesta y la línea base fijan el producto y los cálculos; el plan establece el orden de implementación y verificación. Los documentos de `docs` desarrollan esas fuentes y no las sustituyen.

## Propósito del proyecto

PumpCalc será un simulador web local escrito en Python para explorar cómo cambia el caudal de una bomba al modificar una instalación sencilla. Funcionará como un sandbox con animación 2D. El usuario verá el agua en movimiento y comparará dos configuraciones dentro de un modelo hidráulico idealizado.

La entrega final será un prototipo funcional, ejecutable localmente en un navegador y centrado en una pregunta: **¿qué caudal entregaría esta bomba en esta instalación, según el modelo, y qué cambia al modificar una condición?** El proyecto combinará cálculo numérico propio, agua animada según los resultados y verificaciones reproducibles.

### Problema y utilidad

El caudal de una bomba depende de su interacción con la instalación. El desnivel y las pérdidas de energía en la tubería y los accesorios afectan el punto en que puede operar. PumpCalc permitirá experimentar con esa relación sin montar un equipo físico. El punto de operación se obtendrá al igualar la altura que aporta la bomba y la que exige el sistema [3, 4].

El público inicial serán estudiantes y docentes. Como posibilidad de uso posterior, el mismo enfoque podría apoyar explicaciones preliminares entre instaladores, vendedores y clientes. La propuesta de valor es hacer visible la relación entre configuración, pérdidas y caudal, con una comparación reproducible entre dos escenarios. Su potencial comercial se plantea como una herramienta de demostración y aprendizaje; no se presupone una demanda de mercado ya validada.

### Objetivo general

Desarrollar en Python un simulador web animado de una instalación simple de bombeo que estime su punto de operación mediante métodos numéricos y permita explicar, comparar y verificar los resultados.

### Objetivos específicos

- Representar la curva de la bomba a partir de datos tabulados y calcular la curva de la instalación con unidades consistentes.
- Implementar interpolación lineal, iteración de punto fijo y bisección, mostrando su aporte al resultado y sus criterios de convergencia.
- Comparar dos configuraciones mediante animaciones y resultados, y verificar el modelo con casos de referencia, pruebas numéricas y manejo de entradas inválidas.

### Enfoque de la entrega

El esfuerzo principal se concentrará en un motor de cálculo verificable y una experiencia clara. Esto responde al peso de los fundamentos matemáticos y la programación en la rúbrica, que suman 55 de 100 puntos [2]. El carácter experimental, la comparación de alternativas y la explicación visual aportarán interés y utilidad sin aumentar la complejidad física del problema.

Las secciones 1 a 3 presentan la propuesta y el producto. Las secciones 4 a 10 precisan la animación, el modelo, las pruebas y las condiciones de implementación para desarrollar esa misma entrega.


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


## Representación de la bomba y cálculo de fricción

### Interpolación lineal por tramos

Entre dos puntos consecutivos se calculará la altura de la bomba mediante:

$$
H_b(Q) = H_i + (H_{i+1}-H_i)\frac{Q-Q_i}{Q_{i+1}-Q_i}
$$

La función solo estará definida entre el menor y el mayor caudal ingresados. Se implementará la búsqueda del tramo y la interpolación; la librería gráfica no calculará la curva física. Esta elección conserva los datos, mantiene la monotonía y evita oscilaciones de un polinomio de grado alto. La representación por segmentos también se emplea para curvas multipunto en EPANET [6].

### Iteración de punto fijo para Colebrook

Para Re ≥ 4000 se resolverá Colebrook con la variable x = 1/√f. Al reorganizar la ecuación se obtiene [3]:

$$
x_{n+1} = -2\log_{10}\left(\frac{\varepsilon}{3.7D}+\frac{2.51x_n}{Re}\right), \qquad f = \frac{1}{x^2}
$$

Se iniciará con x₀ = 1/√0,02 y se permitirán hasta 100 iteraciones. Se exigirá que el cambio absoluto entre iteraciones y el valor absoluto del residuo G sean ambos menores o iguales que 10⁻¹⁰, evaluando:

$$
G(x) = x + 2\log_{10}\left(\frac{\varepsilon}{3.7D}+\frac{2.51x}{Re}\right)
$$

Se comprobará que el argumento del logaritmo sea positivo y que los valores calculados sean finitos y x sea positivo. Si no converge, se devolverá un error explícito. Para el dominio admitido, la iteración permanece entre x = 3 y x = 20; en ese intervalo la magnitud de la derivada de la función iterativa no supera 2/(3 ln 10), aproximadamente 0,29. Esta contracción sustenta la convergencia y se comprobará en los extremos del dominio. El método resuelve una incógnita real del modelo con una implementación breve y sin calcular derivadas en el programa.

### Flujo laminar y zona de transición

Para 0 < Re ≤ 2000 se usará f = 64/Re. Para 2000 < Re < 4000 se aplicará una transición continua definida para este prototipo:

$$
t = \frac{Re-2000}{2000}, \qquad f = (1-t)\frac{64}{2000}+t f_{4000}
$$

Aquí f₄₀₀₀ se obtendrá resolviendo Colebrook en Re = 4000 con la misma rugosidad relativa. Esta interpolación será una **decisión didáctica del modelo**, no una ley física de la transición ni el algoritmo de transición de EPANET. Se elige para evitar saltos que dificulten la búsqueda del cruce. Si la solución queda en esa zona, se mostrará una advertencia de aproximación [3, 6].

El factor f se recalculará para cada caudal evaluado. El panel mostrará el tramo interpolado, el régimen y las iteraciones de Colebrook del resultado final. En transición se aclarará que estas corresponden al cálculo auxiliar de f₄₀₀₀; en flujo laminar se indicará que no se requiere iteración.


## Punto de operación y control del error

### Bisección sobre el balance de alturas

El caudal de operación será una raíz de:

$$
F(Q) = H_b(Q)-H_s(Q) = 0
$$

Se usará bisección porque trabaja con funciones continuas, conserva un intervalo que contiene la raíz y ofrece una cota del error sin derivadas [7]. Es adecuada para una curva de bomba lineal por tramos. Con las entradas admitidas, la altura de la bomba no aumenta y la del sistema aumenta con el caudal; por tanto, se espera como máximo un cruce.

El intervalo inicial será exactamente el dominio de la curva ingresada. Primero se evaluarán sus extremos: si uno es raíz se devolverá ese extremo. En otro caso deberá existir cambio de signo. Si ambos valores son negativos, se informará que la curva de la bomba queda por debajo de la del sistema en el intervalo; si ambos son positivos, que queda por encima. Ningún mensaje afirmará que no existe solución fuera de los datos disponibles.

Con cambio de signo se calculará el punto medio c, se evaluará F(c) y se conservará la mitad que mantenga el cambio de signo. Cada registro guardará el intervalo antes de dividirlo. La condición normal de parada exigirá simultáneamente:

$$
\frac{b-a}{2}\leq\tau_Q, \qquad |F(c)|\leq\tau_H
$$

| Control | Valor predeterminado |
| --- | --- |
| Tolerancia de caudal τQ | 10⁻⁷ m³/s equivalente a 0,00036 m³/h |
| Tolerancia de altura τH | 10⁻⁴ m |
| Máximo de iteraciones de bisección | 80 |

Una raíz exacta detectada en un extremo o punto medio podrá finalizar directamente. Si se agota el límite sin cumplir las condiciones, el estado será falta de convergencia. No se confundirá con ausencia de intersección. Las tolerancias serán parámetros internos configurables para las pruebas, sin añadir controles avanzados a la interfaz inicial.

### Evidencia del cálculo

El panel numérico incluirá la tabla de bisección con iteración, a, b, c, F(c) y semiancho del intervalo, además del total de iteraciones, residuo final y tolerancias. Los caudales se mostrarán en m³/h y los residuos en metros. Se incluirá la traza de punto fijo únicamente para el factor de fricción del resultado final, evitando miles de registros de evaluaciones intermedias.

El semiancho es una cota del error de localización de la raíz del modelo, bajo una evaluación suficientemente precisa de F; no mide incertidumbre de la bomba ni de la instalación. Se conservará toda la precisión interna y se redondeará solo al presentar. La gráfica usará 150 muestras por escenario para dibujar, pero el cruce se resolverá con F, nunca buscando el punto visual más cercano.


## Implementación y paquete final

### Estructura suficiente para este alcance

Todo el código de PumpCalc se escribirá en Python, incluidos el motor, la interfaz, las gráficas, la animación y las pruebas. NiceGUI abrirá la aplicación local en el navegador. Las curvas se configurarán en Python con `ui.echart`. La escena usará una capa SVG generada en Python y un temporizador `ui.timer` para mover las trazas [8]. Las pruebas usarán `pytest` [9]. Las versiones de las dependencias se fijarán en `requirements.txt` para instalar el proyecto en un entorno virtual.

El código separará validación, interpolación, fricción, pérdidas, bisección y presentación. El motor usará funciones de Python independientes de la interfaz. La animación tomará sus resultados y avanzará según el tiempo entre fotogramas. Cada escenario conservará su propia copia de entradas, estado, resultados y trazas.

Los tres métodos se implementarán explícitamente. Se permitirán herramientas para interfaz y pruebas, pero ninguna biblioteca resolverá por detrás la interpolación, Colebrook o el punto de operación. No se reemplazarán cálculos por valores de ejemplo: todos los datos editables deberán participar realmente en la simulación.

### Orden de trabajo y entregables

El plan empieza por el modelo y sus pruebas. Luego incorpora el formulario, los estados, las curvas, el detalle numérico y la animación. La comparación de escenarios completa la experiencia. El cierre verificará el recorrido de demostración y documentará la ejecución. Si el tiempo se reduce, se simplificará el acabado visual manteniendo la animación vinculada al cálculo y las verificaciones obligatorias.

La entrega contendrá el código fuente en Python, los tres ejemplos precargados, las pruebas automatizadas y un README con instalación, arranque, pruebas y guía breve de uso. Incluirá una explicación del modelo, las tolerancias, los resultados de validación y las limitaciones para la sustentación.

**Instrucción para el desarrollo.** Implementar el proyecto completo en Python conforme a esta línea base y al plan por pasos. Usar las secciones 2, 4, 5, 6, 7 y 9 como requisitos de alcance, animación, cálculo y aceptación. Resolver decisiones visuales menores con criterio propio. Comprobar las referencias numéricas y la animación antes de dar por terminado el proyecto e informar cualquier comprobación pendiente.

### Referencias

[1] PumpCalc propuesta original. Documento de partida suministrado por el equipo.

[2] Rúbrica de evaluación de proyectos de Métodos Numéricos. Documento suministrado por el equipo, 2 páginas.

[3] Hydraulic Institute. [Pipe Frictional Losses](https://datatool.pumps.org/fluid-flow-iii/general). Darcy, Colebrook, Reynolds y rugosidad.

[4] Hydraulic Institute. [Combined Pump and System Curves](https://datatool.pumps.org/pump-fundamentals/combined). Punto de operación.

[5] Hydraulic Institute. [Losses in Valves Fittings and Bends](https://datatool.pumps.org/fluid-flow-iii/fr-loss-water). Pérdidas localizadas.

[6] US EPA. [EPANET 2.2 The Network Model](https://usepa.github.io/EPANET2.2/3_network_model.html). Curvas y regímenes de flujo. PumpCalc no replica su motor.

[7] University of Waterloo. [Bisection Method Error Analysis](https://eceweb.uwaterloo.ca/~dwharder/NumericalAnalysis/10RootFinding/bisection/error.html).

[8] NiceGUI. [Ejecución local](https://nicegui.io/documentation/section_configuration_deployment), [gráficas](https://nicegui.io/documentation/echart), [escena SVG por capas](https://nicegui.io/documentation/interactive_image) y [temporizador](https://nicegui.io/documentation/timer).

[9] pytest. [Guía de inicio](https://docs.pytest.org/en/stable/getting-started.html).

## Relación con los demás documentos

El alcance funcional está en [Necesidad y requerimientos](NECESIDAD_Y_REQUERIMIENTOS.md); los casos y la aceptación, en [Caso de finca y validación](CASO_FINCA_Y_VALIDACION.md); la presentación y los estados, en [Flujo, arquitectura e interfaz](FLUJO_ARQUITECTURA_E_INTERFAZ.md). Las referencias numeradas anteriores se conservan de la línea base. Las menciones a sus secciones 2, 4, 5, 6, 7, 8 y 9 remiten a la numeración de esa fuente.

La exigencia anterior de conservar intacto `hydraulics.py` queda sustituida por este modelo. La implementación deberá incorporar Darcy–Weisbach, Colebrook por punto fijo y los controles de bisección aquí definidos. La actualización documental no realiza esa migración del código.
