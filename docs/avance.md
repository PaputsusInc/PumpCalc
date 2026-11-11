# Avance de desarrollo de PumpCalc

## Paso 1 Preparar el proyecto local

Fecha: 10 de noviembre de 2026, America/Bogota.

Resultado: entorno `.venv` creado con Python 3.13.7; NiceGUI 4.0.0 y pytest 9.2.0 fijados en `requirements.txt`. `app.py` muestra la vista inicial de PumpCalc en español y escucha en `127.0.0.1:8080`, sin recarga automática. `.gitignore` excluye `.venv`, `__pycache__` y `.pytest_cache`. Los módulos anteriores se conservan sin cambios.

Comprobaciones realizadas:

- `python -m venv .venv`: completado.
- Instalación de NiceGUI y pytest en `.venv`, seguida de `.venv\Scripts\python.exe -m pip install -r requirements.txt`: completada con las versiones fijadas.
- `.venv\Scripts\python.exe -m pip check`: `No broken requirements found.`
- `.venv\Scripts\python.exe -m pytest --version`: `pytest 9.2.0`. No se ejecutó la suite heredada ni se declara validado el motor nuevo; las pruebas numéricas comienzan en el paso 2.
- `.venv\Scripts\python.exe -m py_compile app.py`: sin errores.
- `.venv\Scripts\python.exe app.py`: `NiceGUI ready to go on http://127.0.0.1:8080`.
- Solicitud HTTP a `/`: estado 200 y contenido PumpCalc presente.
- Edge en modo headless con perfil temporal separado: captura de 1440 × 1000 inspeccionada; encabezado, bienvenida y textos visibles sin recortes. El navegador integrado y Computer Use fallaron al iniciar sus auxiliares por permisos del entorno; la comprobación visual se completó con Edge.

El servidor de comprobación se detiene al finalizar. Para abrirlo de nuevo, seguir [INSTALACION_LOCAL.md](INSTALACION_LOCAL.md).

Archivos previstos para el commit de este paso: `.gitignore`, `requirements.txt`, `app.py`, `docs/INSTALACION_LOCAL.md` y `docs/avance.md`. La reorganización y actualización documental previa, incluida la corrección de estado en `docs/README.md`, se mantiene fuera del área de preparación para no mezclar ese trabajo pendiente con el paso 1.

Commit propuesto: `chore: preparar la base local de PumpCalc`. No se crea hasta la siguiente instrucción del usuario según el plan. Al decir «sigamos», verificar el contenido preparado antes de registrar el commit y continuar únicamente con el paso 2, validación de entradas e interpolación de la bomba.
