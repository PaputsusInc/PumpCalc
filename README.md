# PumpCalc

### 1. Problema SItuación
Software del proyecto final de Métodos Numéricos.


### 2. Cómo se configura y actualiza la escena web

En [`escena3d.py`](pumpcalc/escena3d.py), NiceGUI crea una `ui.scene` con dimensiones iniciales de 840 × 470, sin cuadrícula, con fondo `#080f2b`, cámara en perspectiva de 42° y objetivo de **30 FPS**. La cámara inicia en `(0, -13, 5.8)` mirando hacia `(0, 0, 1.28)`; «Restablecer cámara» vuelve a esa posición. El archivo `bomba_usuario.glb` se sirve en `/modelos/bomba_usuario.glb` y se inserta con `escena.gltf(...)`. También se colocan tres luces de acento, las etiquetas, el suelo, la base, ambos depósitos y la tubería.

Esta línea registra el archivo de bomba para que el navegador pueda solicitarlo por URL:

```python
BOMBA_MODELO = Path(__file__).parents[1] / 'assets' / 'modelos' / 'bomba_usuario.glb'
BOMBA_URL = app.add_static_file(local_file=BOMBA_MODELO, url_path='/modelos/bomba_usuario.glb')
```

`BOMBA_MODELO` es la ruta local al GLB exportado y `BOMBA_URL` es la dirección que usará `escena.gltf(BOMBA_URL)` más abajo.

La instalación visible se **reconstruye cuando cambia su geometría**. `geometria_3d(instalacion, tanques)` traduce las entradas a coordenadas de exhibición: el desnivel inicial eleva el nivel de destino, la longitud desplaza ese depósito y el diámetro aumenta el radio dibujado. El volumen inicial como fracción de la capacidad fija el nivel de agua de cada tanque. Las expresiones con logaritmos comprimen los cambios de la instalación para que quepan en pantalla; **no son una escala métrica**. La bomba GLB permanece como modelo fijo. La rugosidad y `K` intervienen en el cálculo hidráulico, pero no cambian la geometría 3D.

Estas son las transformaciones principales, con `L` y `Δz` en metros y `D` en metros:

```python
def geometria_3d(instalacion: Instalacion,
                 tanques: ConfiguracionTanques | None = None) -> Geometria3D:
    desnivel = 2.45 * math.log1p(instalacion.desnivel_m) / math.log1p(100)
    distancia = 0.42 * math.log1p(instalacion.longitud_m / 10) / math.log1p(100)
    radio = 0.082 + 0.052 * math.log(instalacion.diametro_m / 0.01, 20)
    fraccion_origen = .75 if tanques is None else tanques.origen.inicial_m3 / tanques.origen.capacidad_m3
    fraccion_destino = .125 if tanques is None else tanques.destino.inicial_m3 / tanques.destino.capacidad_m3
    nivel_origen = ALTURA_TOMA + ALTURA_VISUAL_AGUA * fraccion_origen
    return Geometria3D(nivel_origen, nivel_origen + desnivel, 3.9 + distancia, radio,
                       fraccion_origen, fraccion_destino)
```

`math.log1p(x)` calcula `ln(1 + x)`. Los niveles iniciales dependen del agua ingresada y mantienen la diferencia visual de altura. Por ejemplo, duplicar `L` desplaza el depósito en pantalla, pero no duplica la distancia dibujada. El valor real de `L` sí entra en las ecuaciones hidráulicas; esta función solo decide la forma de mostrarlo.

Esta es la configuración inicial exacta de la escena en la clase `VistaEscena3D`:

```python
self.escena = ui.scene(
    width=840, height=470, grid=False, background_color='#080f2b',
    camera=ui.scene.perspective_camera(fov=42), fps=30,
).classes('pc-three-canvas').style('width:100%; height:100%;').props(
    'role=img aria-label="Vista 3D de dos depósitos, bomba, tubería y agua que fluye según la velocidad calculada"'
)
self.escena.move_camera(0, -13, 5.8, look_at_x=0, look_at_y=0, look_at_z=1.28, duration=0)
```

`fov=42` es el campo de visión de la cámara en perspectiva; `fps=30` fija el objetivo de actualización. El fondo y la posición de cámara determinan cómo se ve la instalación al abrir la vista; la clase CSS permite ajustarla al espacio disponible.

La tubería se arma con cilindros rectos y codos de Bézier. Cada tramo muestra una envolvente exterior y un interior cian; se agregan dos `CanalAgua` para representar el movimiento dentro de aspiración y descarga. Los depósitos se construyen con base, postes, bordes y paneles transparentes. La escena usa un `SueloLuminoso` y materiales o shaders del navegador para los efectos visuales. Todo eso está definido en Python y en los archivos JavaScript de `pumpcalc/assets/`; no procede del GLB de la bomba.

El siguiente fragmento de `_construir` muestra qué partes se crean en la aplicación y cuál viene del modelo exportado:

```python
tanque(-4.05, g.base_origen, g.nivel_origen, destino=False)
tanque(g.x_destino, g.base_destino, g.nivel_destino, destino=True)

# Línea de aspiración, bomba y descarga. El diámetro mostrado se comprime visualmente.
tubo(-4.16, -1.93, .58)
tubo(.23, 1.92, .58)
```

Esas llamadas forman parte de `_construir`; unas líneas más abajo, en el mismo método, se inserta **el GLB de la bomba**:

```python
# Geometría y materiales PBR procedentes del archivo Blender aportado.
escena.gltf(BOMBA_URL)
```

La distinción importante para exponer es que `tanque(...)` y `tubo(...)` responden a las entradas del usuario, mientras que `escena.gltf(BOMBA_URL)` incorpora la bomba preparada en Blender.

**Cadena de datos de esta versión:** curva e instalación → punto estacionario inicial → volúmenes, capacidades y áreas de los tanques → integración temporal por Runge–Kutta 4 → trayectoria de niveles, caudal y velocidad → reproducción 3D. Python calcula la trayectoria; JavaScript interpola sus muestras entre fotogramas. `AguaEnTuberia` mueve las partículas con la velocidad calculada en cada instante, transformada a unidades visuales por segundo; `SuperficieAgua` y `TanqueLlenado` muestran los niveles derivados de los volúmenes. La vista 2D conserva su animación anterior de niveles fijos.

### Llenado calculado con Runge–Kutta 4

El formulario **Agua inicial · vista 3D** pide, para cada depósito, volumen inicial, capacidad y área horizontal. El desnivel `Δz` del formulario es la diferencia entre las superficies **al comienzo**. Si `V` es el volumen transferido, el desnivel posterior es `Δz + V/A_destino + V/A_origen`. Por conservación de volumen, el origen pierde exactamente lo que gana el destino. La ecuación diferencial es `dV/dt = Q(V)`, donde cada evaluación de `Q(V)` vuelve a resolver el cruce bomba–sistema al desnivel de ese instante.

[`transitorio.py`](pumpcalc/transitorio.py) implementa explícitamente las cuatro etapas `k1`, `k2`, `k3` y `k4` de RK4, con pasos de 10 segundos simulados. La integración se detiene cuando se agota el agua de origen, se llena el destino, deja de existir un cruce en el dominio de la bomba o se alcanza el horizonte de dos horas simuladas. El caso base comienza con 1,2 m³ y 0,2 m³; ambos tanques tienen capacidad 1,6 m³ y área 1 m². La trayectoria termina cerca de 19,69 minutos simulados al agotarse el origen. El visor acelera la reproducción: **un segundo visual equivale a 60 segundos simulados**. El tiempo que muestra es el de la trayectoria calculada, no el tiempo que lleva abierta la página.

La simulación sigue siendo un modelo educativo: supone depósitos de sección horizontal constante, tubería llena, bomba a velocidad fija y flujo cuasiestacionario en cada paso. No modela cebado, cavitación, succión al descubrirse la toma ni transitorios de presión. La geometría dibujada conserva una escala comprimida. La precisión temporal depende del paso de integración y de la curva de bomba disponible.

En código, la rapidez visual y la decisión de activar el flujo son:

```python
def rapidez_3d(velocidad_ms: float) -> float:
    """Escala monótona común a A/B, en unidades visuales por segundo."""
    if not math.isfinite(velocidad_ms) or velocidad_ms < 0:
        raise ValueError('La velocidad debe ser finita y no negativa.')
    return 2.8 * velocidad_ms / (velocidad_ms + 1.8)
```

`punto_vigente` habilita el cálculo temporal solo cuando existe una solución inicial con caudal positivo y los tanques tienen datos válidos. `VistaEscena3D._sincronizar_flujo` prepara una trayectoria nueva únicamente al cambiar la revisión del escenario o de los tanques. [`tanque_llenado.js`](pumpcalc/assets/tanque_llenado.js) reproduce esa trayectoria, informa tiempo, caudal y volúmenes corrientes, y comunica el nivel y la rapidez al resto de los componentes 3D. «Pausar» conserva el instante alcanzado; «Reproducir de nuevo» regresa a los volúmenes iniciales. Si no hay un punto inicial válido, se suspende el movimiento. La vista necesita WebGL.

### 3. Cómo interpretar el análisis de tiempo y recursos

El archivo reciente [`tools/perfil_rendimiento.py`](tools/perfil_rendimiento.py) mide el **funcionamiento de la escena 3D del caso base**, no la duración de un cálculo hidráulico ni el tiempo de llenado. Inicia PumpCalc y Chromium, abre la página a 1440 × 900, espera a que la escena esté visible, deja pasar 2 segundos de estabilización y toma una muestra de 10 segundos por defecto. Reinicia el flujo cada 8 segundos para mantener la animación activa. En Linux lee `/proc` para sumar el servidor y el árbol de procesos de Chromium; el controlador Node de Playwright queda fuera de esa suma. El navegador informa el renderizador WebGL empleado.

**Cómo sale cada cifra del código:** el navegador guarda una marca de tiempo cuando el lienzo WebGL ejecuta `gl.clear`:

```javascript
window.pumpcalcRenderTimes = [];
const original = gl.clear.bind(gl);
gl.clear = (...args) => {
    window.pumpcalcRenderTimes.push(performance.now());
    return original(...args);
};
```

El perfilador toma los ticks de CPU y la memoria `Pss:` de `/proc` para los procesos incluidos:

```python
pids = descendientes(tabla, {servidor_pid, chromium_pid})
ticks = sum(tabla[pid][1] for pid in pids)
pss_kib = 0
```

Finalmente calcula y muestra los indicadores así:

```python
fps = (len(tiempos) - 1) / ((tiempos[-1] - tiempos[0]) / 1000)
cpu = (ticks_finales - ticks_iniciales) / TICKS_POR_SEGUNDO / duracion * 100
print(f'FPS: {fps:.1f}')
print(f'CPU promedio (servidor + Chromium): {cpu:.1f} % de un núcleo')
print(f'Memoria máxima PSS (servidor + Chromium): {pico_pss / 1024:.1f} MiB')
```

`len(tiempos) - 1` cuenta intervalos entre marcas; la resta de marcas está en milisegundos y se divide por 1000 para obtener segundos. Los ticks se convierten a segundos de CPU y luego a porcentaje de **un núcleo**. `pico_pss` está en KiB y se divide por 1024 para mostrar MiB. Son fragmentos del perfilador; entre la inicialización y la impresión, el bucle toma muestras de memoria cada 0,25 segundos y conserva la mayor.

En este equipo, el **12 de noviembre de 2026**, dos ejecuciones reales de 10 segundos en modo con ventana dieron los siguientes resultados **antes de añadir la integración temporal RK4**. Son antecedentes de la escena anterior y no una medición de rendimiento de esta versión:

| Medida | Corrida 1 | Corrida 2 | Lectura para la sustentación |
| --- | ---: | ---: | --- |
| FPS observados | 26,3 | 25,3 | Aproximadamente 25–26 actualizaciones por segundo durante estas muestras. El objetivo configurado es 30 FPS; no significa que siempre se alcance. |
| CPU promedio, servidor + Chromium | 47,5 % | 80,1 % | Consumo equivalente a 0,475 y 0,801 núcleos de CPU, respectivamente. Es porcentaje **de un núcleo**, no del procesador completo. |
| Memoria máxima PSS, servidor + Chromium | 587,3 MiB | 588,7 MiB | Pico aproximado de memoria física atribuible a esos procesos en cada muestra. No es tamaño del GLB ni memoria de la GPU. |

Las dos corridas informaron `ANGLE (Intel, Mesa Intel(R) Graphics (RPL-P), OpenGL 4.6)` como renderizador. **Interpretación de los FPS:** el perfilador registra las llamadas a `gl.clear` del lienzo WebGL y divide los intervalos registrados por el tiempo entre la primera y la última llamada. Es una aproximación a la frecuencia de actualización: 26,3 FPS equivalen a unos **38,0 ms por actualización**, y 25,3 FPS a unos **39,5 ms**. Con un objetivo de 30 FPS, el intervalo ideal sería 33,3 ms. Esta prueba muestra una escena animada cercana, aunque inferior, a ese objetivo en este equipo; no demuestra fluidez constante ni da los peores tiempos de cada fotograma.

**Interpretación de CPU y memoria:** la CPU sale de la diferencia de tiempo de procesador acumulado en `/proc`, dividida por los segundos transcurridos. Puede superar 100 % si varios núcleos trabajan a la vez. La diferencia entre 47,5 % y 80,1 % muestra variación entre ejecuciones; no conviene presentarla como un consumo fijo. PSS reparte entre procesos la memoria de páginas compartidas y se consulta aproximadamente cada 0,25 segundos; el valor mostrado es el máximo observado, de modo que un pico más breve podría no quedar capturado. Estos números dependen del equipo, el renderizador, la carga del sistema, el tamaño de ventana y el modo de ejecución.

Para repetir la medición en Linux, con Chromium, una sesión gráfica y Playwright disponibles, ejecuta desde `PumpCalc`:

```bash
.venv/bin/python tools/perfil_rendimiento.py --segundos 10
```

`--headless` permite ejecutarlo sin ventana, pero puede cambiar el renderizador y volver las cifras no comparables con las anteriores. La conclusión defendible es: **en estas dos muestras del caso base, la animación 3D rondó 25–26 FPS, usó menos de un núcleo de CPU en promedio y ocupó cerca de 588 MiB PSS entre servidor y navegador**. El script no mide arranque, latencia al editar entradas, duración del solucionador, consumo de GPU ni tiempo real de traslado del agua.

## Acerca de PumpCalc

PumpCalc es un simulador web local escrito en Python. Estima cuánto caudal entrega una bomba a través de una tubería entre dos depósitos abiertos. Puedes cambiar una condición de la instalación, comparar dos escenarios y ver tanto el movimiento del agua como los pasos del cálculo.

## Estructura del proyecto

| Carpeta | Contenido |
| --- | --- |
| `pumpcalc/` | Cálculo e interfaz web; `pumpcalc/assets/` contiene las animaciones 3D. |
| `assets/modelos/` | Modelo GLB de la bomba que usa la vista 3D. |
| `tools/blender/` | Script para extraer la bomba del archivo Blender, fuera de la aplicación en ejecución. |
| `tests/` | Pruebas de la app web y del cálculo; `legacy/` reúne las de escritorio. |
| `docs/` | Guías y documentación; `antecedentes/` guarda los documentos iniciales. |

`app.py` inicia la aplicación web. `main.py` conserva la entrada de escritorio anterior.

## Instalación en Windows

Necesitas Python 3.13 y un navegador. El proyecto se verificó con Python 3.13.7 y 3.13.15. Abre PowerShell en la carpeta de PumpCalc y ejecuta estos comandos. Usa `py -3.13` para crear el entorno: el comando `python` puede apuntar a otra instalación de Python. Después, ejecuta siempre el intérprete de `.venv`.

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Con el servidor en ejecución, abre <http://127.0.0.1:8080> en el navegador. Para detenerlo, pulsa `Ctrl+C` en la terminal. En las siguientes sesiones puedes arrancar con el tercer comando.

Si `python app.py` falla antes de iniciar NiceGUI, comprueba qué versión devuelve `python --version` y ejecuta `.\.venv\Scripts\python.exe app.py` desde esta carpeta. El arranque local no requiere compilar el proyecto ni tener Docker instalado.

## Ejecutar con Docker

Desde la carpeta de PumpCalc:

```bash
docker compose up --build
```

Abre <http://localhost:8080>. Para detenerlo, pulsa `Ctrl+C`; para retirar el contenedor, ejecuta `docker compose down`. También puedes construir y ejecutar sin Compose con `docker build -t pumpcalc .` y `docker run --rm -p 8080:8080 pumpcalc`.

## Primer experimento

1. Abre el **Caso base** en A. La tubería mide 40 m, su diámetro interno es de 25 mm y el desnivel es de 12 m. El caudal estimado es de aproximadamente 3,765450 m³/h.
2. Pulsa **Copiar A en B**, cambia el diámetro de B a 32 mm y activa **Comparar A y B**. Espera el recálculo automático o pulsa **Simular**.
3. Compara las cifras y las escenas. El selector **3D / 2D** cambia ambas vistas sin alterar el cálculo. En 3D puedes girar la instalación y restablecer la cámara. En B pasan unos 4,381752 m³/h, pero el agua avanza a 1,513406 m/s frente a 2,130809 m/s en A. El área de la tubería crece más que el caudal, así que la velocidad disminuye.
4. Vuelve a copiar A en B y cambia únicamente la longitud a 80 m. El recorrido dibujado se alarga y las trazas se ralentizan. También puedes cambiar el desnivel para mover el depósito de destino, o cambiar la rugosidad y K para observar las pérdidas indicadas en la escena.
5. Abre **Detalle numérico** para ver el tramo de interpolación, el residuo y la cota de bisección, y las iteraciones de Colebrook cuando correspondan. Carga **Sin intersección** en B para ver cómo se presenta un caso sin cruce dentro del intervalo de la curva de la bomba.
6. En **Agua inicial · vista 3D**, cambia el volumen inicial del origen de 1,2 a 0,5 m³. La trayectoria 3D se reinicia y termina antes; el caudal estacionario inicial permanece igual. Observa el tiempo simulado, el caudal instantáneo y los dos volúmenes bajo la escena.

La curva de demostración es ficticia. Los indicadores principales corresponden al punto **estacionario inicial**. La vista 2D mantiene niveles fijos. La vista 3D integra el cambio de volumen y vuelve a calcular el caudal al variar el desnivel; sus etiquetas muestran el estado transitorio. «Reproducir de nuevo» restablece los volúmenes iniciales. El tiempo estimado depende de los supuestos del modelo y no certifica una instalación real. Si Q = 0 hay solución sin movimiento; si faltan datos válidos o no hay cruce, se suspende el movimiento sin suponer Q = 0. La vista 3D requiere WebGL. A y B se guardan en memoria mientras la página está abierta.

En «Curva de la bomba» puedes anotar opcionalmente la potencia nominal del motor (HP), la altura máxima Hmax (m) y el caudal máximo Qmax (m³/h). Son datos de referencia independientes para A y B: se copian con «Copiar A en B» y se muestran en la comparación. No sustituyen los pares caudal–altura ni modifican el cálculo. Hmax y Qmax no representan un mismo punto de funcionamiento.

## Cómo funciona el cálculo

1. [entradas.py](pumpcalc/entradas.py) valida los datos y convierte milímetros a metros y m³/h a m³/s. Así, las ecuaciones reciben unidades coherentes. La curva exige caudales crecientes y alturas que no aumenten.
2. [interpolacion.py](pumpcalc/interpolacion.py) calcula la altura de la bomba `Hb(Q)` en el segmento que contiene el caudal. Por ejemplo, entre 2 m³/h a 31 m y 3 m³/h a 26 m, la altura para 2,5 m³/h es 28,5 m.
3. [perdidas.py](pumpcalc/perdidas.py) calcula el área, la velocidad y Reynolds. Suma el desnivel y las pérdidas de tubería y accesorios para obtener `Hs(Q)`. [friccion.py](pumpcalc/friccion.py) obtiene el factor de Darcy mediante `64/Re` en régimen laminar, punto fijo de Colebrook en turbulento y una unión didáctica en transición.
4. [operacion.py](pumpcalc/operacion.py) usa [biseccion.py](pumpcalc/biseccion.py) para encontrar dónde `Hb(Q) − Hs(Q) = 0` dentro del intervalo de la curva. Para aceptar una raíz aproximada se exige un semiancho de hasta `1e-7 m³/s` y un residuo de hasta `1e-4 m`. El resultado conserva las iteraciones y el tramo que usó el interpolador para calcular la altura de la bomba.

### Ejecutar el motor desde Python

Abre `.\.venv\Scripts\python.exe` desde la raíz y pega este ejemplo en el intérprete.

```python
from dataclasses import replace

from pumpcalc.ejemplos import caso_base
from pumpcalc.operacion import resolver_operacion

base = caso_base()
tuberia_ancha = replace(
    base, instalacion=replace(base.instalacion, diametro_m=0.032)
)

for nombre, escenario in (("A", base), ("B", tuberia_ancha)):
    resultado = resolver_operacion(escenario)
    punto = resultado.punto
    if punto is None:
        print(f"{nombre} | {resultado.mensaje}")
        continue
    print(
        f"{nombre} | Q = {punto.caudal_m3s * 3600:.6f} m³/h"
        f" | H = {punto.altura_m:.6f} m"
        f" | v = {punto.sistema.velocidad_ms:.6f} m/s"
    )
```

```text
A | Q = 3.765450 m³/h | H = 20.641853 m | v = 2.130809 m/s
B | Q = 4.381752 m³/h | H = 15.564232 m | v = 1.513406 m/s
```

Aquí `replace` crea un segundo escenario a partir de A, con el diámetro expresado en metros. El motor devuelve `punto=None` cuando no hay una solución dentro del dominio o falla la convergencia. Un resultado válido con caudal cero sí tiene un punto.

## Cómo se conecta la interfaz

| Parte | Dónde leer el código | Qué resuelve |
| --- | --- | --- |
| Arranque y vista | [app.py](app.py), [vista.py](pumpcalc/vista.py), [tema.py](pumpcalc/tema.py) | Abren NiceGUI y conectan el formulario con los resultados. |
| Edición y comparación | [simulacion.py](pumpcalc/simulacion.py), [comparacion.py](pumpcalc/comparacion.py), [ejemplos.py](pumpcalc/ejemplos.py) | Conservan entradas independientes por escenario y recalculan tras 200 ms sin cambios válidos. La meta se compara con el caudal calculado. |
| Resultados y gráficas | [resultados.py](pumpcalc/resultados.py), [presentacion.py](pumpcalc/presentacion.py), [detalle.py](pumpcalc/detalle.py), [panel_comparacion.py](pumpcalc/panel_comparacion.py) | Presentan el resultado vigente y las iteraciones. La vista individual y la comparación comparten la preparación de las curvas. |
| Llenado 3D y animación | [transitorio.py](pumpcalc/transitorio.py), [animacion.py](pumpcalc/animacion.py), [escena.py](pumpcalc/escena.py), [escena3d.py](pumpcalc/escena3d.py), [componentes 3D](pumpcalc/assets), [modelo 3D](assets/modelos/bomba_usuario.glb) | Runge–Kutta 4 calcula la trayectoria de volúmenes, caudal y velocidad; el navegador la reproduce en la escena 3D. La vista 2D conserva sus trazas de niveles fijos. |
| Versión de escritorio anterior | [main.py](main.py), [pumpcalc/ui/](pumpcalc/ui/), [casos_uso.py](pumpcalc/casos_uso.py), [hydraulics.py](pumpcalc/hydraulics.py), [persistencia.py](pumpcalc/persistencia.py) | Usa CustomTkinter, calcula dos condiciones del tanque mediante Hazen–Williams y guarda escenarios en SQLite. |

## Pruebas

```powershell
.\.venv\Scripts\python.exe -m pytest
```

La carpeta [tests](tests/) cubre casos numéricos de referencia, validación, estados de A/B, escena y eventos de NiceGUI. Con las dependencias web, pytest omite el módulo de pruebas de la ventana de escritorio si falta CustomTkinter.

## Documentación y comprobaciones

- [Manual, modelo y tutorial del motor](docs/README.md).
- [Guía de sustentación](docs/GUIA_SUSTENTACION.md).
- [Informe de verificación y aceptación manual](docs/VALIDACION_FINAL.md).
- [Registro de desarrollo](docs/avance.md).

## Diagramas del código

### Componentes del sistema

![Componentes del sistema](docs/diagramas/01_componentes.svg)

### Flujo del punto de operación

![Flujo del punto de operación](docs/diagramas/02_flujo_operacion.svg)

### Evaluación de F(Q)

![Evaluación de F(Q)](docs/diagramas/03_evaluacion_f.svg)

### Ciclo de una sesión

![Ciclo de una sesión](docs/diagramas/04_ciclo_sesion.svg)
