# PumpCalc decisiones cerradas y pendientes de implementación

**Estado documental:** especificación vigente, sincronizada el 10 de noviembre de 2026. Describe la entrega requerida; no certifica que el código existente ya la implemente.

Fuentes de verdad: [propuesta v4](../Baseline%20y%20pasos/PumpCalc%20propuesta%20v4.docx), [línea base con animación](../Baseline%20y%20pasos/PumpCalc_linea_base_Codex_con_animacion.md) y [plan de desarrollo por pasos](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md). La propuesta y la línea base fijan el producto y los cálculos; el plan establece el orden de implementación y verificación. Los documentos de `docs` desarrollan esas fuentes y no las sustituyen.

## Decisiones que ya están cerradas

El inventario anterior abría decisiones que ahora resuelven las fuentes. Estos puntos no requieren una nueva definición de producto para comenzar el desarrollo.

| Tema | Decisión vigente |
| --- | --- |
| Plataforma | Python y NiceGUI, web local en navegador, servidor en 127.0.0.1. |
| Público y propósito | Estudiantes y docentes; experimentación y explicación del punto de operación. |
| Navegación | Una vista principal; selección A/B mediante pestañas o controles equivalentes. |
| Inicio | Caso base cargado, calculado y animado. |
| Entradas | L, D interno, Δz, ε y K total; curva de 3 a 10 puntos en m³/h y m. |
| Modelo | Darcy–Weisbach, Colebrook por punto fijo, interpolación lineal y bisección. |
| Escenarios | A y B independientes en memoria, copia A → B, sin guardado persistente. |
| Meta | Opcional y común; evaluación separada con margen y cota numérica. |
| Actualización | Invalidación al editar y recálculo tras 200 ms; Simular inmediato. |
| Animación | Obligatoria, escena SVG desde Python, trazas según v, escala común y pausa visual. |
| Curvas | 150 muestras por escenario, dominio propio y cruce resuelto por el motor. |
| Explicación | Panel desplegable con tolerancias, residuo, bisección y fricción del resultado final. |
| Validación | Referencias de la línea base, pruebas del motor y recorrido visual; sin exigir mediciones de finca. |
| Fuera de alcance | Base de datos, importación/exportación, catálogos, selección automática, llenado de tanques y publicación obligatoria. |

## Decisiones menores por resolver durante la implementación

La línea base autoriza resolver detalles visuales con criterio propio. Son elecciones de ejecución, no bloqueos previos ni cambios de alcance.

| Detalle | Restricción que debe respetar |
| --- | --- |
| Distribución, tamaños, tipografía y colores | Vista clara en computador, unidades y estados legibles. |
| Pestañas o selector A/B | Mantener dos configuraciones independientes e identificar el escenario activo. |
| Edición y eliminación de filas | Conservar entre 3 y 10 puntos y señalar errores sin corregirlos silenciosamente. |
| Geometría y trazas de la escena | Esquema sin escala geométrica, diámetro perceptible, movimiento ilustrativo según s(v). |
| Frecuencia del temporizador | Avance según tiempo entre fotogramas; actualizar solo las trazas usando el resultado vigente. |
| Redondeo visible | Conservar precisión interna y no ocultar el estado En el límite numérico. |
| Archivos y módulos | Separar motor de presentación y evitar complejidad innecesaria. |

## Secuencia de desarrollo y aceptación

| Paso | Trabajo | Comprobación de cierre |
| --- | --- | --- |
| 1 | Preparar entorno, versiones y vista NiceGUI. | `python app.py` inicia y abre la vista local. |
| 2 | Validación, conversiones e interpolación. | Nodos, 28,5 m en 2,5 m³/h, sin extrapolación y entradas inválidas. |
| 3 | Fricción y pérdidas. | Caudal cero, laminar, referencia turbulenta, continuidad y errores de convergencia. |
| 4 | Bisección y punto de operación. | Raíz analítica, A/B, longitud, desnivel, extremos y ambos casos sin cambio de signo. |
| 5 | Formulario y resultados. | Recálculo, errores e invalidación comprobados en navegador. |
| 6 | Curvas y detalle numérico. | Coincidencia de marcador e indicadores, dominio y trazas. |
| 7 | Animación. | D de 25 a 32 mm aumenta el grosor y reduce la velocidad; pausa y suspensión correctas. |
| 8 | Comparación y meta. | A intacto al editar B, ejemplos, meta de 4 m³/h y comparación sin datos inventados. |
| 9 | Entrega y sustentación. | Entorno limpio, pytest, recorrido completo y documentación de comprobaciones reales. |

Este cuadro resume el [plan de desarrollo](../Baseline%20y%20pasos/PumpCalc_plan_de_desarrollo_por_pasos.md); no marca pasos completados. Al retomar la implementación se revisará lo existente y se verificará el primer paso pendiente.

## Ritmo de trabajo definido por el plan

Se implementará un paso por turno y se verificará antes de preparar sus cambios en Git. Desde el paso 2 se ejecutará `python -m pytest`; al cambiar interfaz se comprobará en navegador. Se registrarán las verificaciones reales en `docs/avance.md`. Preparar un commit significa revisar sus cambios preparados con `git diff --cached`, sin registrarlo todavía ni incluir trabajo previo del usuario.

Cuando el usuario diga «sigamos», se revisará que los cambios preparados sigan siendo los mostrados, se registrará el commit local y se continuará únicamente con el paso siguiente. Si los cambios preparados difieren o el commit falla, se informará y se detendrá el avance. Si el paso actual no estaba listo, se retomará primero. «Ajusta…» corrige el paso actual; «haz el commit» lo registra y espera. No se duplican commits ni se hacen commits vacíos. No habrá push, despliegue ni PR sin petición. Al terminar el último paso, «sigamos» registra el último commit y cierra la entrega.

Estas reglas rigen el desarrollo por pasos. La presente actualización de `docs` es una sincronización documental solicitada por separado; no completa el paso 1, no prepara un commit de implementación ni certifica el producto.
