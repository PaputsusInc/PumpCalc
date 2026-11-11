# PumpCalc

PumpCalc será un simulador web local en Python y NiceGUI para explorar el caudal de una bomba en una instalación simple. La entrega incluye animación 2D vinculada a la velocidad calculada, comparación de escenarios A/B y explicación de interpolación lineal, Colebrook por punto fijo y bisección.
**Estado documental:** especificación vigente, sincronizada el 10 de noviembre de 2026. Describe la entrega requerida; no certifica que el código existente ya la implemente.

Fuentes de verdad: [propuesta v4](../Baseline%20y%20pasos/PumpCalc%20propuesta%20v4.docx), [línea base con animación](../Baseline%20y%20pasos/PumpCalc_linea_base_Codex_con_animacion.md) y [plan de desarrollo por pasos](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md). La propuesta y la línea base fijan el producto y los cálculos; el plan establece el orden de implementación y verificación. Los documentos de `docs` desarrollan esas fuentes y no las sustituyen.

## Estado del repositorio y de esta documentación

Los documentos de esta carpeta describen la especificación vigente. La aplicación [app.py](../app.py) incorpora el motor de cálculo, el formulario de un escenario, las curvas y el detalle numérico hasta el paso 6. Usa NiceGUI 4.0.0 y pytest 9.2.0, fijados en [requirements.txt](../requirements.txt), con Python 3.13.7 en Windows. La guía de arranque está en [Instalación local](INSTALACION_LOCAL.md) y las comprobaciones reales y la revisión visual pendiente en [avance](avance.md).

El código anterior se conserva: [main.py](../main.py) inicia CustomTkinter, [hydraulics.py](../pumpcalc/hydraulics.py) usa Hazen–Williams y [persistencia.py](../pumpcalc/persistencia.py) usa SQLite. La aplicación web utiliza los módulos nuevos de validación, interpolación, fricción, pérdidas y bisección. La animación y la comparación A/B corresponden a los pasos 7 y 8; las dependencias de la aplicación antigua no forman parte del nuevo entorno.

## Instalación y ejecución local

Estos comandos se ejecutan desde la raíz del repositorio para abrir la aplicación local:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abre `http://127.0.0.1:8080` en el navegador. El servidor NiceGUI escucha solo en `127.0.0.1`. Con el entorno activado, los comandos de arranque y pruebas son `python app.py` y `python -m pytest`. Las pruebas numéricas de la nueva entrega comienzan en el paso 2 y la instalación final en un entorno limpio se verifica en el paso 9.

## Uso previsto

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

En B sube Q y baja v de 2,130805 a 1,513408 m/s: la tubería será más ancha y las trazas avanzarán más despacio. A no alcanza la meta de 4 m³/h; B sí. L = 80 m es una prueba adicional, no un cuarto ejemplo precargado obligatorio. Estos valores proceden de la línea base y no son mediciones ni resultados ejecutados durante esta actualización.

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

La siguiente actividad de desarrollo deberá revisar y retomar el primer paso pendiente del plan. Esta actualización conserva las fuentes de verdad y los cambios previos del usuario; no registra commits ni declara pasos de implementación terminados.
