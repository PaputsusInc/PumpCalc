"""Valida y calcula las dos condiciones de tanque de la aplicación de escritorio."""

import math
from itertools import pairwise

from pumpcalc.hydraulics import altura_instalacion, punto_operacion


MATERIALES = {"PVC": 150, "Acero": 120, "Hierro fundido": 100}
ACCESORIOS = {
    "Codos de 90°": 0.9,
    "Válvulas de compuerta abiertas": 0.15,
    "Válvulas de retención": 2.5,
}
UNIDADES = {"m³/h": 1.0, "L/min": 0.06, "US gpm": 0.22712472}


class ErrorEntrada(ValueError):
    def __init__(self, campo, mensaje):
        super().__init__(mensaje)
        self.campo = campo


def _numero(datos, clave, etiqueta, minimo=0, positivo=False):
    try:
        valor = float(str(datos.get(clave, "")).strip().replace(",", "."))
    except (ValueError, TypeError):
        raise ErrorEntrada(clave, f"{etiqueta}: escribe un número válido.") from None
    if not math.isfinite(valor) or valor < minimo or (positivo and valor == 0):
        condicion = "mayor que cero" if positivo else f"mayor o igual a {minimo:g}"
        raise ErrorEntrada(clave, f"{etiqueta}: debe ser {condicion}.")
    return valor


def _leer_accesorios(datos):
    """Lee cantidades enteras en el orden del catálogo que muestra el formulario."""
    cantidades = {}
    for indice, nombre in enumerate(ACCESORIOS):
        clave = f"accesorio_{indice}"
        texto = str(datos.get(clave, "")).strip()
        try:
            valor = int(texto)
        except ValueError:
            raise ErrorEntrada(clave, f"{nombre}: escribe una cantidad entera.") from None
        if valor < 0:
            raise ErrorEntrada(clave, f"{nombre}: la cantidad no puede ser negativa.")
        cantidades[nombre] = valor
    return cantidades


def _leer_curva(datos, factor_caudal):
    """Convierte el texto de la curva a pares en m³/h y metros."""
    puntos = []
    for indice, linea in enumerate(str(datos.get("puntos", "")).splitlines(), 1):
        if not linea.strip():
            continue
        partes = linea.split(";")
        if len(partes) != 2:
            raise ErrorEntrada("puntos", f"Curva, línea {indice}: usa caudal; altura.")
        try:
            q, h = (float(parte.strip().replace(",", ".")) for parte in partes)
        except ValueError:
            raise ErrorEntrada("puntos", f"Curva, línea {indice}: escribe dos números válidos.") from None
        if not math.isfinite(q) or not math.isfinite(h) or q < 0 or h < 0:
            raise ErrorEntrada("puntos", f"Curva, línea {indice}: caudal y altura deben ser finitos y no negativos.")
        puntos.append((q * factor_caudal, h))
    if len(puntos) < 2:
        raise ErrorEntrada("puntos", "Curva: introduce al menos dos pares caudal; altura.")
    for (caudal_anterior, altura_anterior), (caudal, altura) in pairwise(puntos):
        if caudal <= caudal_anterior or altura > altura_anterior:
            raise ErrorEntrada("puntos", "Curva: ordena por caudal creciente y altura no creciente.")
    return puntos


def validar_entradas(datos):
    """Devuelve números listos para el cálculo o un error asociado a su campo."""
    longitud = _numero(datos, "longitud", "Longitud de tubería", positivo=True)
    diametro = _numero(datos, "diametro", "Diámetro interior", positivo=True)
    vacio = _numero(datos, "desnivel_vacio", "Desnivel con tanque casi vacío")
    lleno = _numero(datos, "desnivel_lleno", "Desnivel con tanque casi lleno")
    material = datos.get("material")
    if material not in MATERIALES:
        raise ErrorEntrada("material", "Selecciona un material válido.")
    cantidades = _leer_accesorios(datos)
    unidad = datos.get("unidad")
    if unidad not in UNIDADES:
        raise ErrorEntrada("unidad", "Elige m³/h, L/min o US gpm. Si la ficha solo dice GPM, aclara el tipo de galón.")
    puntos = _leer_curva(datos, UNIDADES[unidad])
    return {
        "longitud": longitud, "diametro": diametro,
        "desnivel_vacio": vacio, "desnivel_lleno": lleno,
        "material": material, "cantidades": cantidades, "puntos": puntos,
        "suma_k": sum(cantidades[n] * k for n, k in ACCESORIOS.items()),
    }


def _condicion(datos, desnivel):
    puntos = datos["puntos"]
    instalacion = {
        "longitud_m": datos["longitud"],
        "diametro_mm": datos["diametro"],
        "coeficiente_c": MATERIALES[datos["material"]],
        "desnivel_m": desnivel,
        "suma_k": datos["suma_k"],
    }
    resultado = punto_operacion(puntos, **instalacion)
    if resultado is not None:
        return {"estado": "cruce", "resultado": resultado,
                "mensaje": "Caudal y velocidad estimados para esta condición."}
    q_primero, h_primera = puntos[0]
    q_ultimo, h_ultima = puntos[-1]
    f_primero = h_primera - altura_instalacion(q_primero, **instalacion)["total_m"]
    f_ultimo = h_ultima - altura_instalacion(q_ultimo, **instalacion)["total_m"]
    if q_primero == 0 and f_primero < 0:
        return {"estado": "altura_insuficiente", "resultado": None,
                "mensaje": "La bomba no vence la altura estática ni a caudal cero, según esta curva."}
    if f_ultimo > 0:
        mensaje = "La bomba aún supera la altura requerida en el último punto. Faltan datos a caudales mayores."
    elif f_primero < 0:
        mensaje = "La curva empieza por debajo de la altura requerida. Podrían faltar datos a caudales menores."
    else:
        mensaje = "No se encontró cruce dentro de la curva ingresada. Faltan datos para decidir."
    return {"estado": "sin_cruce", "resultado": None, "mensaje": mensaje}


def calcular_escenario(entradas):
    """Estima el caudal por separado con el tanque casi vacío y casi lleno."""
    datos = validar_entradas(entradas)
    condiciones = {
        "vacio": _condicion(datos, datos["desnivel_vacio"]),
        "lleno": _condicion(datos, datos["desnivel_lleno"]),
    }
    vacio = condiciones["vacio"]["resultado"]
    lleno = condiciones["lleno"]["resultado"]
    if vacio and lleno:
        resumen = (f"Caudal estimado: {vacio['caudal_m3h']:.3f} m³/h con el tanque casi vacío "
                   f"y {lleno['caudal_m3h']:.3f} m³/h casi lleno.")
    elif vacio or lleno:
        condicion = "casi vacío" if vacio else "casi lleno"
        resumen = f"Solo se pudo estimar el caudal con el tanque {condicion}; revisa la otra condición."
    else:
        resumen = "No se pudo estimar el caudal en ninguna condición con la curva proporcionada."
    return {"datos": datos, "condiciones": condiciones, "resumen": resumen}


def firma_calculo(entradas):
    """Campos que modifican el cálculo."""
    claves = ("longitud", "diametro", "desnivel_vacio", "desnivel_lleno",
              "material", "unidad", "puntos", "accesorio_0", "accesorio_1", "accesorio_2")
    return {clave: str(entradas.get(clave, "")).strip() for clave in claves}
