# PumpCalc

PumpCalc es un simulador web local en Python y NiceGUI para explorar el caudal de una bomba en una instalación simple. Incluye animación 2D vinculada a la velocidad calculada, comparación de escenarios A/B y explicación de interpolación lineal, Colebrook por punto fijo y bisección.
**Estado al 11 de noviembre de 2026:** paso 9 completado con instalación limpia, pruebas automatizadas y aceptación visual comunicada por el usuario. La evidencia y el alcance de esa aceptación están en el [informe de verificación](VALIDACION_FINAL.md).

Después de ese cierre se incorporó, por solicitud del usuario, una nueva presentación visual de laboratorio: azul profundo, turquesa y lima, controles junto a la simulación, indicadores destacados y escenas sobre fondo oscuro. El tema local está en [tema.py](../pumpcalc/tema.py). Las 282 pruebas pasan con el rediseño; su apariencia aún no ha sido observada directamente por el agente ni aceptada de nuevo por el usuario. La aceptación anterior corresponde a la versión de cierre.

Fuentes de verdad: [propuesta v4](../Baseline%20y%20pasos/PumpCalc%20propuesta%20v4.docx), [línea base con animación](../Baseline%20y%20pasos/PumpCalc_linea_base_Codex_con_animacion.md) y [plan de desarrollo por pasos](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md). La propuesta y la línea base fijan el producto y los cálculos; el plan establece el orden de implementación y verificación. Los documentos de `docs` desarrollan esas fuentes y no las sustituyen.

## Estado del repositorio y de esta documentación

Los documentos de esta carpeta describen la especificación vigente. La aplicación [app.py](../app.py) incorpora el motor de cálculo, los escenarios A/B independientes, las curvas, el detalle numérico, la animación 2D y la meta común. Usa NiceGUI 4.0.0 y pytest 9.2.0, fijados en [requirements.txt](../requirements.txt), con Python 3.13.7 en Windows. La guía de arranque está en [Instalación local](INSTALACION_LOCAL.md) y las comprobaciones reales y la aceptación manual en [avance](avance.md).

El código anterior se conserva: [main.py](../main.py) inicia CustomTkinter, [hydraulics.py](../pumpcalc/hydraulics.py) usa Hazen–Williams y [persistencia.py](../pumpcalc/persistencia.py) usa SQLite. La aplicación web utiliza los módulos nuevos de validación, interpolación, fricción, pérdidas y bisección. Permite copiar A en B, cargar tres ejemplos en el escenario activo y comparar resultados y animaciones con una escala común. La meta solo cambia su evaluación. Las dependencias de la aplicación antigua no forman parte del nuevo entorno.

## Instalación y ejecución local

Estos comandos se ejecutan desde la raíz del repositorio para abrir la aplicación local:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abre `http://127.0.0.1:8080` en el navegador. El servidor NiceGUI escucha solo en `127.0.0.1`; `Ctrl+C` lo detiene. No necesitas activar el entorno ni cambiar la política de ejecución de PowerShell. Si el puerto está ocupado, detén la instancia anterior desde su terminal.

Para comprobar dependencias y ejecutar las pruebas:

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m pytest
```

Para repetir la instalación limpia, elige otra carpeta de entorno que todavía no exista y sustituye `.venv` en los comandos. Se verificó `.tmp\entrega-limpia-20261111` con Python 3.13.7, NiceGUI 4.0.0 y pytest 9.2.0: **282 pruebas aprobadas y 1 módulo heredado de interfaz omitido** por ausencia de CustomTkinter. La omisión no corresponde a NiceGUI. El entorno y los registros temporales están excluidos de Git.

## Uso

1. Abrir el caso base A, calculado y animado.
2. Cambiar longitud, diámetro interno, desnivel, rugosidad, K total o la curva de bomba. Se recalcula tras 200 ms sin cambios válidos; Simular actúa inmediatamente.
3. Copiar A en B y cambiar una condición para comparar cifras, curvas y movimiento.
4. Introducir, si se desea, una meta común y consultar margen y estado sin alterar el punto de operación.
5. Consultar métodos, tolerancias e iteraciones, o pausar la animación sin cambiar el cálculo.

Las entradas de la curva usan m³/h y m; el motor convierte a SI. La curva admite entre 3 y 10 puntos y no se extrapola. Cada escenario tiene niveles fijos y conserva sus datos solo en memoria. Recargar restaura el ejemplo inicial.

## Ejemplos y resultados de referencia

Curva ficticia común en (m³/h, m): `(0, 35)`, `(1, 34)`, `(2, 31)`, `(3, 26)`, `(4, 19)`, `(5, 10)`. Caso base: L = 40 m, D = 25 mm, Δz = 12 m, ε = 0,0015 mm, K = 4 y meta opcional de 4 m³/h.

| Ejemplo precargado | Cambio respecto de A | Q esperado | H esperada |
| --- | --- | --- | --- |
| Caso base A | Ninguno | 3,765443 m³/h | 20,641896 m |
| Cambio de diámetro B | D = 32 mm | 4,381758 m³/h | 15,564175 m |
| Sin intersección | Δz = 40 m | No aplica | No aplica |

Los valores de la tabla son referencias de la línea base. En la ejecución del entorno limpio se observaron Q = 3,765449524 m³/h y H = 20,641853333 m en A, y Q = 4,381752014 m³/h y H = 15,564231873 m con D = 32 mm. Ambos cumplen errores absolutos máximos de 0,001 m³/h y 0,001 m frente a las referencias.

En B sube Q y baja v de 2,130808550 a 1,513406017 m/s: el área aumenta con D² y v = Q/área disminuye. La representación usa una tubería más ancha y trazas más lentas. A no alcanza la meta de 4 m³/h; B sí. B − A = 0,616302490 m³/h, un 16,367301867 % respecto de A. L = 80 m es una prueba adicional, no un cuarto ejemplo precargado. Los datos son ficticios, no mediciones físicas.

## Entradas y unidades

Se acepta coma o punto decimal, sin separadores de miles. Vacío y cero son distintos. El motor recibe metros y m³/s: las conversiones de mm y m³/h se hacen al validar.

| Entrada | Unidad visible | Límites |
| --- | --- | --- |
| Longitud L | m | 0 < L ≤ 1000; L ≥ Δz |
| Diámetro interno D | mm | 10 ≤ D ≤ 200 |
| Desnivel Δz | m | 0 ≤ Δz ≤ 100 |
| Rugosidad ε | mm | 0 ≤ ε ≤ 1; además ε/D ≤ 0,05 |
| K total | Sin unidad | 0 ≤ K ≤ 100 |
| Caudal de cada punto | m³/h | 0 ≤ Q ≤ 100; estrictamente creciente |
| Altura de cada punto | m | 0 ≤ H ≤ 200; no creciente |
| Caudal objetivo | m³/h | Opcional; si se ingresa, 0 < Q ≤ 100 |

La curva requiere entre 3 y 10 puntos. Los datos no se ordenan ni corrigen silenciosamente. Copiar A en B crea una copia independiente; cargar un ejemplo solo afecta al activo. Una entrada inválida, un cálculo pendiente o la ausencia de solución retiran las cifras anteriores como resultados vigentes y suspenden el movimiento. Una solución válida con Q = 0 conserva ese significado. El objetivo vacío significa sin meta; cambiarlo no recalcula el punto de operación.

## Cómo se conectan los métodos

Se usan g = 9,81 m/s² y ν = 1,004 × 10⁻⁶ m²/s. Para cada Q se calcula área = πD²/4, v = Q/área y Re = vD/ν. El balance es:

```text
hf = f (L/D) v²/(2g)
hK = K v²/(2g)
Hs(Q) = Δz + hf + hK
F(Q) = Hb(Q) − Hs(Q)
```

1. **Interpolación lineal por tramos:** obtiene Hb entre dos nodos de bomba y reproduce los nodos. Con el ejemplo, Hb(2,5 m³/h) = 28,5 m.
2. **Punto fijo de Colebrook:** obtiene el factor de Darcy turbulento usando x = 1/√f y `x_nuevo = −2 log10(ε/(3,7D) + 2,51x_anterior/Re)`. Ese factor entra en hf. Para Re ≤ 2000 se usa 64/Re; entre 2000 y 4000 se interpola entre f₂₀₀₀ y el auxiliar de Colebrook f₄₀₀₀, con advertencia didáctica. En Q = 0 no se evalúa fricción: Hs = Δz y f no aplica.
3. **Bisección:** busca F(Q) = 0 en el dominio ingresado de bomba, evaluando interpolación y pérdidas en cada caudal. El punto calculado alimenta indicadores, marcador y animación. Las muestras de la gráfica no intervienen en la búsqueda.

| Control | Valor y condición |
| --- | --- |
| Colebrook | x₀ = 1/√0,02; máximo 100 iteraciones |
| Parada de Colebrook | Cambio absoluto y residuo absoluto ≤ 10⁻¹⁰, ambos |
| Bisección | Máximo 80 iteraciones |
| Parada de bisección | Semiancho ≤ 10⁻⁷ m³/s y residuo absoluto ≤ 10⁻⁴ m, ambos |
| Raíz exacta | Se acepta en extremo o punto medio con cota cero |
| Meta | Margen Q − objetivo; si su valor absoluto no supera la cota de la raíz, estado **En el límite numérico** |

Sin cambio de signo se informa la posición relativa de las curvas en el intervalo disponible. Si se agotan iteraciones, se informa falta de convergencia. Ninguna de esas situaciones se sustituye por caudal cero. La cota mide error numérico del solver, no incertidumbre física.

La gráfica une los nodos de bomba con segmentos rectos y muestra 150 muestras del sistema en su dominio. El marcador viene directamente del solver. La animación mantiene niveles fijos y mueve trazas según el tiempo transcurrido con `s(v) = 240v/(v+2)` px/s. El grosor crece con D mediante `8 + 12 log₂(D/0,01)` px, con D en metros. Ambas escalas son comunes a A/B. La longitud modifica el recorrido y el desnivel mueve el depósito de destino. El esquema muestra la rugosidad, K y las pérdidas calculadas. Los niveles quedan fijos durante cada escenario. Pausar y reanudar controlan el movimiento de las trazas.

## Tutorial mínimo del motor

Guarda este ejemplo en un archivo Python en la raíz y ejecútalo con el intérprete del entorno. No necesita iniciar NiceGUI:

```python
from pumpcalc.ejemplos import caso_base
from pumpcalc.operacion import resolver_operacion

resultado = resolver_operacion(caso_base())
if resultado.punto is None:
    print(resultado.estado, resultado.mensaje)
else:
    punto = resultado.punto
    print("Q (m³/h):", punto.caudal_m3s * 3600)
    print("H (m):", punto.altura_m)
    print("v (m/s):", punto.sistema.velocidad_ms)
    print("Residuo (m):", resultado.biseccion.residuo)
```

Para construir datos visibles se usan `validar_instalacion` y `validar_curva` de [entradas.py](../pumpcalc/entradas.py), que devuelven objetos SI o `ErrorEntrada` con el campo afectado. [operacion.py](../pumpcalc/operacion.py) coordina [interpolacion.py](../pumpcalc/interpolacion.py), [perdidas.py](../pumpcalc/perdidas.py), [friccion.py](../pumpcalc/friccion.py) y [biseccion.py](../pumpcalc/biseccion.py), sin depender de la interfaz.

[simulacion.py](../pumpcalc/simulacion.py) mantiene el estado y las revisiones; [comparacion.py](../pumpcalc/comparacion.py) coordina A/B y meta. [vista.py](../pumpcalc/vista.py) conecta los controles con [presentacion.py](../pumpcalc/presentacion.py), [detalle.py](../pumpcalc/detalle.py), [panel_comparacion.py](../pumpcalc/panel_comparacion.py) y las escenas de [animacion.py](../pumpcalc/animacion.py) y [escena.py](../pumpcalc/escena.py).

## Documentos

| Documento | Contenido y trazabilidad principal |
| --- | --- |
| [Documento del proyecto](DOCUMENTO_PROYECTO.md) | Propósito, ecuaciones, métodos, tolerancias e implementación; línea base §§1, 5–7 y 10. |
| [Necesidad y requerimientos](NECESIDAD_Y_REQUERIMIENTOS.md) | Público, alcance, dominios, requisitos e historias; línea base §§1–3 y 5. |
| [Flujo, arquitectura e interfaz](FLUJO_ARQUITECTURA_E_INTERFAZ.md) | Estado por escenario, vista principal, curvas y animación; línea base §§3–4 y 10, pasos 5–8. |
| [Caso de finca y validación](CASO_FINCA_Y_VALIDACION.md) | Casos reproducibles, pruebas y sustentación; línea base §§8–9 y paso 9. El nombre se conserva por compatibilidad. |
| [Pendientes de diseño](PENDIENTES_DE_DISENO.md) | Decisiones ya cerradas, detalles menores y secuencia de nueve pasos; línea base y plan. |

## Contraste con la documentación anterior

| Tema | Documentación anterior sustituida | Especificación vigente |
| --- | --- | --- |
| Público | Responsable de finca como usuario principal. | Estudiantes y docentes; uso comercial posterior solo como posibilidad. |
| Plataforma | Escritorio CustomTkinter y `main.py`. | Web local NiceGUI y `app.py`. |
| Pérdidas | Hazen–Williams y coeficientes C por material. | Darcy–Weisbach, ε directo y Colebrook por punto fijo. |
| Accesorios | Cantidades y catálogo de K. | K total agregado, sin coeficientes ocultos. |
| Escenario | Dos condiciones de llenado por configuración. | Un desnivel por escenario; A y B independientes, niveles fijos. |
| Curva | Al menos dos puntos y unidades seleccionables. | De 3 a 10 puntos, m³/h y m, sin extrapolación. |
| Meta | Ausente o inconsistente entre documentos. | Opcional, común y con estado En el límite numérico. |
| Guardado | SQLite, borradores y biblioteca de escenarios. | Solo memoria; recargar restaura el caso inicial. |
| Experiencia | Paneles de escritorio y recálculo manual. | Vista única, actualización tras 200 ms y animación obligatoria según v. |
| Solver | Hasta 60 iteraciones y parada por uno de dos criterios. | Hasta 80, semiancho ≤ 10⁻⁷ m³/s y residuo ≤ 10⁻⁴ m simultáneamente, salvo raíz exacta. |
| Casos | Q ≈ 6,064 y 6,616 m³/h con otra curva y modelo. | Q ≈ 3,765443 y 4,381758 m³/h con la curva vigente. |
| Restricción al código | Conservar intacto el motor anterior. | Implementar explícitamente los tres métodos de la línea base. |

## Límites

Se modelan agua a aproximadamente 20 °C, una bomba centrífuga a velocidad fija y una tubería llena entre depósitos abiertos. No se incluyen redes, múltiples bombas, velocidad variable, llenado temporal, cavitación, NPSH, eficiencia, consumo, costos, optimización, cuentas, base de datos, importación/exportación ni publicación obligatoria. La animación es ilustrativa; alcanzar la meta no certifica una instalación real.

El cierre incluye una [guía de sustentación](GUIA_SUSTENTACION.md), un [informe de verificación](VALIDACION_FINAL.md) y el [registro de avance](avance.md). La aceptación visual del recorrido fue comunicada por el usuario; el agente no pudo observar directamente el navegador.
