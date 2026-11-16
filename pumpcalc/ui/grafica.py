"""Dibujo de la bomba y de las dos curvas de instalación."""

from pumpcalc.casos_uso import MATERIALES
from pumpcalc.hydraulics import altura_instalacion


def dibujar(canvas, calculo):
    """Proyecta caudal y altura al lienzo de la aplicación de escritorio."""
    canvas.delete("all")
    if not calculo:
        return
    datos = calculo["datos"]
    puntos = datos["puntos"]
    ancho = max(canvas.winfo_width(), 560)
    alto = max(canvas.winfo_height(), 320)
    x0, x1, y0, y1 = 62, ancho - 25, 25, alto - 58
    q0, q1 = puntos[0][0], puntos[-1][0]

    def sistema(q, desnivel):
        return altura_instalacion(q, datos["longitud"], datos["diametro"],
                                  MATERIALES[datos["material"]], desnivel,
                                  datos["suma_k"])["total_m"]

    max_h = max([h for _, h in puntos] +
                [sistema(q1, datos["desnivel_vacio"]), sistema(q1, datos["desnivel_lleno"]), 1]) * 1.1

    def x(q):
        return x0 + (q - q0) * (x1 - x0) / (q1 - q0)

    def y(h):
        # En el lienzo, las coordenadas verticales crecen hacia abajo.
        return y1 - h * (y1 - y0) / max_h

    for i in range(6):
        yy = y(max_h * i / 5)
        xx = x(q0 + (q1 - q0) * i / 5)
        canvas.create_line(x0, yy, x1, yy, fill="#e5edf2")
        canvas.create_line(xx, y0, xx, y1, fill="#eff3f6")
        canvas.create_text(x0 - 7, yy, text=f"{max_h * i / 5:.0f}", anchor="e", fill="#607688")
        canvas.create_text(xx, y1 + 15, text=f"{q0 + (q1 - q0) * i / 5:.1f}", fill="#607688")
    canvas.create_text((x0 + x1) / 2, alto - 14, text="Caudal (m³/h)", fill="#324b60")
    canvas.create_text(16, (y0 + y1) / 2, text="Altura (m)", angle=90, fill="#324b60")

    def trazo(coordenadas, color, grosor=3):
        for a, b in zip(coordenadas, coordenadas[1:]):
            canvas.create_line(x(a[0]), y(a[1]), x(b[0]), y(b[1]), fill=color, width=grosor)

    trazo(puntos, "#1673b1")
    colores = {"vacio": "#dc852f", "lleno": "#9b57ad"}
    for clave, desnivel in (("vacio", datos["desnivel_vacio"]), ("lleno", datos["desnivel_lleno"])):
        trazo([(q0 + (q1 - q0) * i / 120, sistema(q0 + (q1 - q0) * i / 120, desnivel))
               for i in range(121)], colores[clave])
        resultado = calculo["condiciones"][clave]["resultado"]
        if resultado:
            q, h = resultado["caudal_m3h"], resultado["total_m"]
            canvas.create_oval(x(q) - 6, y(h) - 6, x(q) + 6, y(h) + 6,
                               fill=colores[clave], outline="white", width=2)
    for i, (texto, color) in enumerate((("Bomba", "#1673b1"),
                                        ("Tanque casi vacío", colores["vacio"]),
                                        ("Tanque casi lleno", colores["lleno"]))):
        yy = y0 + 8 + 18 * i
        canvas.create_line(x1 - 145, yy, x1 - 125, yy, fill=color, width=3)
        canvas.create_text(x1 - 119, yy, text=texto, anchor="w", fill="#324b60")
