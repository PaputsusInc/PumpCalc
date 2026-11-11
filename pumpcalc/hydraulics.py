"""Modelo de Hazen–Williams para la versión de escritorio anterior.

Unidades internas: caudal en m³/h, longitud y altura en m, diámetro en mm.
La ecuación de Hazen-Williams se evalúa con Q en m³/s y D en m.
"""


GRAVEDAD = 9.81
PI = 3.141592653589793


def altura_instalacion(caudal_m3h, longitud_m, diametro_mm, coeficiente_c,
                       desnivel_m, suma_k):
    """Devuelve velocidad y alturas de pérdida para un caudal dado."""
    caudal_m3s = caudal_m3h / 3600.0
    diametro_m = diametro_mm / 1000.0
    area_m2 = PI * diametro_m * diametro_m / 4.0
    velocidad_ms = caudal_m3s / area_m2

    # Hazen–Williams usa el coeficiente C del material para la pérdida lineal.
    perdida_tuberia_m = (
        10.67 * longitud_m * caudal_m3s ** 1.852
        / (coeficiente_c ** 1.852 * diametro_m ** 4.871)
    )
    perdida_accesorios_m = suma_k * velocidad_ms ** 2 / (2.0 * GRAVEDAD)
    altura_total_m = desnivel_m + perdida_tuberia_m + perdida_accesorios_m

    return {
        "velocidad_ms": velocidad_ms,
        "tuberia_m": perdida_tuberia_m,
        "accesorios_m": perdida_accesorios_m,
        "total_m": altura_total_m,
    }


def altura_bomba(caudal_m3h, punto_izquierdo, punto_derecho):
    """Interpola linealmente la altura entre dos puntos medidos de la bomba."""
    q0, h0 = punto_izquierdo
    q1, h1 = punto_derecho
    return h0 + (h1 - h0) * (caudal_m3h - q0) / (q1 - q0)


def punto_operacion(puntos_bomba, longitud_m, diametro_mm, coeficiente_c,
                    desnivel_m, suma_k):
    """Encuentra el cruce en un segmento de la curva mediante bisección.

    Devuelve None cuando no existe cruce en el intervalo suministrado.
    Los puntos se reciben ordenados por caudal creciente.
    """
    for indice in range(len(puntos_bomba) - 1):
        izquierdo = puntos_bomba[indice]
        derecho = puntos_bomba[indice + 1]

        def diferencia(caudal):
            bomba = altura_bomba(caudal, izquierdo, derecho)
            instalacion = altura_instalacion(
                caudal, longitud_m, diametro_mm, coeficiente_c, desnivel_m, suma_k
            )["total_m"]
            return bomba - instalacion

        bajo, alto = izquierdo[0], derecho[0]
        f_bajo = diferencia(bajo)
        f_alto = diferencia(alto)

        if abs(f_bajo) <= 1e-9:
            caudal = bajo
        elif abs(f_alto) <= 1e-9:
            caudal = alto
        elif f_bajo * f_alto > 0:
            continue
        else:
            for _ in range(60):
                medio = (bajo + alto) / 2.0
                f_medio = diferencia(medio)
                if abs(f_medio) <= 1e-9 or alto - bajo <= 1e-8:
                    break
                if f_bajo * f_medio <= 0:
                    alto = medio
                else:
                    bajo = medio
                    f_bajo = f_medio
            caudal = (bajo + alto) / 2.0

        resultado = altura_instalacion(
            caudal, longitud_m, diametro_mm, coeficiente_c, desnivel_m, suma_k
        )
        resultado["caudal_m3h"] = caudal
        resultado["altura_bomba_m"] = altura_bomba(caudal, izquierdo, derecho)
        return resultado

    return None

