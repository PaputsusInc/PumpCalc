FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PUMPCALC_HOST=0.0.0.0 \
    PUMPCALC_PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY pumpcalc/ ./pumpcalc/
COPY assets/modelos/bomba_usuario.glb ./assets/modelos/bomba_usuario.glb

EXPOSE 8080

CMD ["python", "app.py"]
