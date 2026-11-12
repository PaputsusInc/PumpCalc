# PumpCalc

PumpCalc es un simulador web local escrito en Python. Estima cuánto caudal entrega una bomba a través de una tubería entre dos depósitos abiertos. Puedes cambiar una condición de la instalación, comparar dos escenarios y ver tanto el movimiento del agua como los pasos del cálculo.

## Instalación en Windows

Necesitas Python 3.13.7, la versión verificada para este proyecto, y un navegador. Abre PowerShell en la carpeta de PumpCalc y ejecuta estos comandos. El primero crea el entorno virtual. El segundo instala NiceGUI y pytest con las versiones indicadas en [requirements.txt](requirements.txt).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Con el servidor en ejecución, abre <http://127.0.0.1:8080> en el navegador. Para detenerlo, pulsa `Ctrl+C` en la terminal. En las siguientes sesiones puedes arrancar con el tercer comando.

## Primer experimento

1. Abre el **Caso base** en A. La tubería mide 40 m, su diámetro interno es de 25 mm y el desnivel es de 12 m. El caudal estimado es de aproximadamente 3,765450 m³/h.
2. Pulsa **Copiar A en B**, cambia el diámetro de B a 32 mm y activa **Comparar A y B**. Espera el recálculo automático o pulsa **Simular**.
3. Compara las cifras y las escenas. El selector **3D / 2D** cambia ambas vistas sin alterar el cálculo. En 3D puedes girar la instalación y restablecer la cámara. En B pasan unos 4,381752 m³/h, pero el agua avanza a 1,513406 m/s frente a 2,130809 m/s en A. El área de la tubería crece más que el caudal, así que la velocidad disminuye.
4. Vuelve a copiar A en B y cambia únicamente la longitud a 80 m. El recorrido dibujado se alarga y las trazas se ralentizan. También puedes cambiar el desnivel para mover el depósito de destino, o cambiar la rugosidad y K para observar las pérdidas indicadas en la escena.
5. Abre **Detalle numérico** para ver el tramo de interpolación, el residuo y la cota de bisección, y las iteraciones de Colebrook cuando correspondan. Carga **Sin intersección** en B para ver cómo se presenta un caso sin cruce dentro del intervalo de la curva de la bomba.

La curva de demostración es ficticia. El cálculo hidráulico es estacionario y usa niveles de referencia fijos. La vista 2D mantiene esos niveles; la 3D muestra una transferencia ilustrativa: baja el nivel en succión y sube en descarga, con rapidez relativa dependiente de la velocidad calculada. «Reproducir de nuevo» restablece la secuencia. Los niveles mostrados y la parada visual no predicen un tiempo de llenado ni una parada física de la bomba. Si Q = 0 hay solución sin movimiento; si faltan datos válidos o no hay cruce, se suspende el movimiento sin suponer Q = 0. La vista 3D requiere WebGL en el navegador. A y B se guardan en memoria mientras la página está abierta.

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
| Animación | [animacion.py](pumpcalc/animacion.py), [escena.py](pumpcalc/escena.py), [escena3d.py](pumpcalc/escena3d.py), [assets](pumpcalc/assets) | La vista 2D mueve trazas desde Python. La vista 3D dibuja agua, bomba y depósitos con Three.js y anima el flujo en el navegador según la velocidad calculada. |
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
