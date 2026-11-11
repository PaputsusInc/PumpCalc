# PumpCalc Simulador de bombeo

Propuesta de simulador de bombeo y línea base para su desarrollo

## 1 Propósito del proyecto

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

---

## 2 Alcance de la entrega final

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

---

## 3 Experiencia de uso y resultados

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

---

## 4 Animación 2D del agua

### Representación visible

La escena mostrará agua azul dentro de una tubería llena y pequeñas trazas o partículas que recorran continuamente su interior desde el origen hasta el destino. El movimiento deberá ser perceptible durante el uso, sin depender de una imagen o un video precalculado. La tubería será más ancha al aumentar el diámetro; longitud y desnivel aparecerán rotulados en un esquema que no estará a escala geométrica.

Los niveles de los depósitos permanecerán fijos. La animación representará el flujo estacionario calculado, sin simular el llenado de tanques ni el arranque físico de la bomba. Se utilizará una escena prediseñada, sin editor de circuitos, dibujo libre, simulación 3D ni dinámica computacional de fluidos.

### Movimiento vinculado al modelo

Las trazas avanzarán según la velocidad media v obtenida de Q y del área de la tubería. No se asignará una rapidez visual arbitraria a cada ejemplo. Para mantener el movimiento legible se usará una escala ilustrativa común a ambos escenarios:

$$
s(v) = 240\frac{v}{v+2}
$$

En esta expresión, v se introduce en m/s; 2 representa una velocidad de referencia de 2 m/s y 240 el límite visual en píxeles por segundo. Así, s vale cero cuando v es cero, aumenta continuamente con v y comprime las velocidades grandes. Los indicadores conservarán Q y v en sus unidades físicas. La escena indicará **Movimiento ilustrativo**, sin atribuir una escala física al recorrido en pantalla.

La misma relación se aplicará a A y B, sin normalizar cada escena por separado. Un mayor caudal no implica necesariamente mayor velocidad: al aumentar el diámetro puede crecer Q y disminuir v. La animación deberá reflejar esa diferencia; no cambiará las revoluciones de la bomba, que se modela a velocidad fija.

### Interacción y estados

Después de 200 ms sin cambios en entradas válidas del modelo se recalculará el escenario activo. La animación, las curvas y los indicadores tomarán juntos el nuevo resultado. **Simular** ejecutará ese cálculo inmediatamente. Un temporizador de NiceGUI actualizará desde Python solo la capa de trazas con el resultado vigente. Modificar solo el caudal objetivo actualizará la evaluación de la meta.

Habrá un control **Pausar animación** y **Reanudar animación**. La pausa será solo visual: no apagará la bomba ni modificará los resultados. Si hay datos inválidos, cálculo pendiente, falta de convergencia o ausencia de cruce, se suspenderá el movimiento y se mostrará el estado correspondiente. La ausencia de solución no se convertirá en un supuesto caudal cero. Una solución válida con Q = 0 se representará sin movimiento.

Al comparar se mostrarán dos vistas compactas de la misma escena, con las etiquetas de Q, v y D. Copiar A en B producirá inicialmente el mismo movimiento; al modificar B, A conservará su configuración y resultado. El usuario podrá ver qué cambia sin perder la referencia inicial.

---

## 5 Entradas y modelo hidráulico

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

---

## 6 Representación de la bomba y cálculo de fricción

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

---

## 7 Punto de operación y control del error

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

---

## 8 Casos reproducibles y valores de referencia

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

---

## 9 Verificación y condiciones de aceptación

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

---

## 10 Implementación y paquete final

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
