"""Mide la animación 3D de PumpCalc sin modificar la aplicación.

Uso desde la carpeta PumpCalc::

    .venv/bin/python tools/perfil_rendimiento.py
    .venv/bin/python tools/perfil_rendimiento.py --segundos 15

Requiere Linux, Chromium, una sesión gráfica y Playwright para Python.
Si falta Playwright: uv pip install --python .venv/bin/python playwright
CPU y memoria abarcan el servidor y el árbol de procesos de Chromium.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import urlopen


RAIZ = Path(__file__).resolve().parents[1]
PROC = Path('/proc')
TICKS_POR_SEGUNDO = os.sysconf('SC_CLK_TCK') if sys.platform == 'linux' else 0


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--segundos', type=float, default=10.0,
                        help='duración de la muestra con la animación activa (por defecto: 10)')
    parser.add_argument('--chromium', type=Path,
                        help='ruta al ejecutable de Chromium; se detecta automáticamente si se omite')
    parser.add_argument('--headless', action='store_true',
                        help='ejecutar sin ventana; puede usar renderizado por software')
    args = parser.parse_args()
    if not 1 <= args.segundos <= 300:
        parser.error('--segundos debe estar entre 1 y 300')
    return args


def puerto_disponible() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def esperar_servidor(url: str, proceso: subprocess.Popen[bytes]) -> None:
    limite = time.monotonic() + 30
    while time.monotonic() < limite:
        if proceso.poll() is not None:
            raise RuntimeError(f'PumpCalc terminó antes de responder (código {proceso.returncode}).')
        try:
            with urlopen(url, timeout=0.5) as respuesta:
                if respuesta.status == 200:
                    return
        except (OSError, URLError):
            time.sleep(0.1)
    raise RuntimeError('PumpCalc no respondió en 30 segundos.')


def tabla_procesos() -> dict[int, tuple[int, int]]:
    """Devuelve PID -> (PPID, tiempo de CPU en ticks)."""
    tabla = {}
    for carpeta in PROC.iterdir():
        if not carpeta.name.isdigit():
            continue
        try:
            bruto = (carpeta / 'stat').read_text()
            campos = bruto[bruto.rfind(')') + 2:].split()
            tabla[int(carpeta.name)] = (int(campos[1]), int(campos[11]) + int(campos[12]))
        except (OSError, ValueError, IndexError):
            continue  # El proceso puede terminar mientras se lee /proc.
    return tabla


def descendientes(tabla: dict[int, tuple[int, int]], raices: set[int]) -> set[int]:
    encontrados = set(raices)
    pendientes = list(raices)
    while pendientes:
        padre = pendientes.pop()
        for pid, (ppid, _) in tabla.items():
            if ppid == padre and pid not in encontrados:
                encontrados.add(pid)
                pendientes.append(pid)
    return encontrados & tabla.keys()


def encontrar_chromium(tabla: dict[int, tuple[int, int]]) -> int:
    """Localiza el navegador creado por Playwright; excluye su controlador Node."""
    for pid in descendientes(tabla, {os.getpid()}):
        try:
            ejecutable = Path(os.readlink(PROC / str(pid) / 'exe')).name
            padre = Path(os.readlink(PROC / str(tabla[pid][0]) / 'exe')).name
        except OSError:
            continue
        if ejecutable in {'chromium-browser', 'chromium', 'chrome', 'google-chrome', 'chrome-stable'} \
                and padre in {'node', 'nodejs'}:
            return pid
    raise RuntimeError('No se encontró el proceso principal de Chromium.')


def muestra(servidor_pid: int, chromium_pid: int) -> tuple[int, int]:
    """CPU acumulada y memoria proporcional PSS del servidor y Chromium."""
    tabla = tabla_procesos()
    pids = descendientes(tabla, {servidor_pid, chromium_pid})
    ticks = sum(tabla[pid][1] for pid in pids)
    pss_kib = 0
    for pid in pids:
        try:
            linea = next(linea for linea in (PROC / str(pid) / 'smaps_rollup').read_text().splitlines()
                          if linea.startswith('Pss:'))
            pss_kib += int(linea.split()[1])
        except (OSError, StopIteration, ValueError):
            continue
    return ticks, pss_kib


def medir(segundos: float, chromium: Path, headless: bool) -> None:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError('Falta Playwright. Instálalo con: '
                           'uv pip install --python .venv/bin/python playwright') from error

    puerto = puerto_disponible()
    url = f'http://127.0.0.1:{puerto}/'
    entorno = dict(os.environ, PUMPCALC_HOST='127.0.0.1', PUMPCALC_PORT=str(puerto))
    servidor = subprocess.Popen([sys.executable, str(RAIZ / 'app.py')], cwd=RAIZ,
                                env=entorno, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        esperar_servidor(url, servidor)
        with sync_playwright() as playwright:
            opciones = ['--enable-webgl']
            if not headless:
                opciones.append('--ozone-platform=x11')
            navegador = playwright.chromium.launch(executable_path=str(chromium),
                                                    headless=headless, args=opciones)
            try:
                pagina = navegador.new_page(viewport={'width': 1440, 'height': 900})
                errores_js = []
                pagina.on('pageerror', lambda error: errores_js.append(str(error)))
                pagina.goto(url, wait_until='networkidle', timeout=30000)
                lienzo = pagina.locator('.pc-scene-a canvas').first
                lienzo.wait_for(timeout=15000)
                escena_a = pagina.locator('.pc-scene-a')
                escena_a.get_by_text('Pausar animación').wait_for(timeout=15000)
                reproducir = escena_a.get_by_text('Reproducir de nuevo')
                renderizador = lienzo.evaluate('''canvas => {
                    const gl = canvas.getContext('webgl2');
                    if (!canvas.offsetWidth || !gl) return null;
                    const ext = gl.getExtension('WEBGL_debug_renderer_info');
                    return ext ? gl.getParameter(ext.UNMASKED_RENDERER_WEBGL) : 'WebGL2';
                }''')
                if not renderizador:
                    raise RuntimeError('La escena 3D no tiene un lienzo WebGL2 visible.')
                time.sleep(2)  # Evita mezclar la carga inicial con el funcionamiento estable.
                reproducir.click()  # Comienza la muestra desde el inicio del flujo.
                lienzo.evaluate('''canvas => {
                    const gl = canvas.getContext('webgl2');
                    window.pumpcalcRenderTimes = [];
                    const original = gl.clear.bind(gl);
                    gl.clear = (...args) => {
                        window.pumpcalcRenderTimes.push(performance.now());
                        return original(...args);
                    };
                }''')
                chromium_pid = encontrar_chromium(tabla_procesos())
                inicio = time.monotonic()
                proximo_reinicio = inicio + 8
                ticks_iniciales, _ = muestra(servidor.pid, chromium_pid)
                pico_pss = 0
                while time.monotonic() - inicio < segundos:
                    if time.monotonic() >= proximo_reinicio:
                        reproducir.click()  # Mantiene el agua en movimiento en muestras largas.
                        proximo_reinicio += 8
                    _, pss = muestra(servidor.pid, chromium_pid)
                    pico_pss = max(pico_pss, pss)
                    time.sleep(0.25)
                ticks_finales, pss = muestra(servidor.pid, chromium_pid)
                pico_pss = max(pico_pss, pss)
                duracion = time.monotonic() - inicio
                tiempos = pagina.evaluate('window.pumpcalcRenderTimes')
                if len(tiempos) < 2:
                    raise RuntimeError('No se observaron fotogramas WebGL durante la medición.')
                if errores_js:
                    raise RuntimeError(f'Error de JavaScript: {errores_js[0]}')
                fps = (len(tiempos) - 1) / ((tiempos[-1] - tiempos[0]) / 1000)
                cpu = (ticks_finales - ticks_iniciales) / TICKS_POR_SEGUNDO / duracion * 100
                print(f'Escena 3D · caso base · {segundos:g} s · {renderizador}')
                print(f'FPS: {fps:.1f}')
                print(f'CPU promedio (servidor + Chromium): {cpu:.1f} % de un núcleo')
                print(f'Memoria máxima PSS (servidor + Chromium): {pico_pss / 1024:.1f} MiB')
            finally:
                navegador.close()
    finally:
        servidor.terminate()
        try:
            servidor.wait(timeout=5)
        except subprocess.TimeoutExpired:
            servidor.kill()
            servidor.wait()


def main() -> int:
    args = argumentos()
    if sys.platform != 'linux':
        print('Este perfilador usa /proc y requiere Linux.', file=sys.stderr)
        return 2
    navegador = args.chromium or next(
        (Path(ruta) for nombre in ('chromium-browser', 'chromium', 'google-chrome')
         if (ruta := shutil.which(nombre))), None
    )
    if navegador is None or not navegador.is_file():
        print('No se encontró Chromium; indica su ruta con --chromium.', file=sys.stderr)
        return 2
    try:
        medir(args.segundos, navegador, args.headless)
    except Exception as error:
        print(f'No se pudo medir PumpCalc: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
