"""Formularios de instalación y bomba, independientes de la navegación."""

import tkinter as tk

import customtkinter as ctk

from pumpcalc.casos_uso import ACCESORIOS, MATERIALES, UNIDADES


TEXTO = "#193247"
SECUNDARIO = "#61788a"
BORDE = "#dce6ec"


class Formulario:
    """Conserva texto editable hasta que la capa de cálculo valida los datos."""

    def __init__(self, al_cambiar):
        self.al_cambiar = al_cambiar
        self.variables = {}
        self.controles = {}
        self.valores_iniciales = {}
        self.filas_curva = []
        self.contenedor_filas = None
        self.aviso_ejemplo = None

    def _variable(self, clave, valor=""):
        variable = tk.StringVar(value=valor)
        variable.trace_add("write", lambda *_: self.al_cambiar())
        self.variables[clave] = variable
        self.valores_iniciales[clave] = valor
        return variable

    @staticmethod
    def _cabecera(parent, paso, titulo, descripcion):
        ctk.CTkLabel(parent, text=paso, text_color="#2a847c", anchor="w",
                     font=ctk.CTkFont(size=12, weight="bold")).pack(fill="x", pady=(4, 3))
        ctk.CTkLabel(parent, text=titulo, text_color=TEXTO, anchor="w",
                     font=ctk.CTkFont(size=26, weight="bold")).pack(fill="x")
        ctk.CTkLabel(parent, text=descripcion, text_color=SECUNDARIO, anchor="w",
                     justify="left", wraplength=770).pack(fill="x", pady=(3, 12))

    @staticmethod
    def _seccion(parent, numero, titulo, descripcion=""):
        tarjeta = ctk.CTkFrame(parent, fg_color="white", corner_radius=14,
                               border_width=1, border_color=BORDE)
        tarjeta.pack(fill="x", padx=(2, 8), pady=7)
        interior = ctk.CTkFrame(tarjeta, fg_color="transparent")
        interior.pack(fill="x", padx=22, pady=18)
        ctk.CTkLabel(interior, text=f"{numero}  {titulo}", text_color=TEXTO,
                     anchor="w", font=ctk.CTkFont(size=17, weight="bold")).pack(fill="x")
        if descripcion:
            ctk.CTkLabel(interior, text=descripcion, text_color=SECUNDARIO,
                         anchor="w", justify="left", wraplength=740).pack(fill="x", pady=(3, 10))
        return interior

    @staticmethod
    def _rejilla(parent, columnas=2):
        rejilla = ctk.CTkFrame(parent, fg_color="transparent")
        rejilla.pack(fill="x")
        rejilla.grid_columnconfigure(tuple(range(columnas)), weight=1, uniform="campo")
        return rejilla

    def _campo(self, parent, clave, etiqueta, fila, columna=0, columnas=1, placeholder=""):
        caja = ctk.CTkFrame(parent, fg_color="transparent")
        caja.grid(row=fila, column=columna, columnspan=columnas, sticky="ew", padx=(0, 14), pady=5)
        ctk.CTkLabel(caja, text=etiqueta, text_color=TEXTO, anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(fill="x", pady=(0, 4))
        variable = self._variable(clave)
        entrada = ctk.CTkEntry(caja, textvariable=variable, height=38,
                               placeholder_text=placeholder, border_color="#cbd8e0")
        entrada.pack(fill="x")
        self.controles[clave] = entrada
        return entrada

    def _opcion(self, parent, clave, etiqueta, opciones, fila, columna=0, columnas=1):
        caja = ctk.CTkFrame(parent, fg_color="transparent")
        caja.grid(row=fila, column=columna, columnspan=columnas, sticky="ew", padx=(0, 14), pady=5)
        ctk.CTkLabel(caja, text=etiqueta, text_color=TEXTO, anchor="w",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(fill="x", pady=(0, 4))
        variable = self._variable(clave, opciones[0])
        control = ctk.CTkOptionMenu(caja, variable=variable, values=opciones, height=38,
                                    fg_color="#edf4f7", button_color="#dae9ee",
                                    button_hover_color="#c9dfe6", text_color=TEXTO)
        control.pack(fill="x")
        self.controles[clave] = control
        return control

    @staticmethod
    def _nota(parent, texto):
        ctk.CTkLabel(parent, text=texto, text_color=SECUNDARIO, anchor="w",
                     justify="left", wraplength=740).pack(fill="x", pady=(8, 0))

    def _plegable(self, parent, titulo):
        boton = ctk.CTkButton(parent, text=f"▸  {titulo}", anchor="w", height=42,
                              fg_color="#e8f0f4", hover_color="#d9e7ed", text_color=TEXTO)
        boton.pack(fill="x", padx=(2, 8), pady=(8, 3))
        contenido = ctk.CTkFrame(parent, fg_color="white", corner_radius=14,
                                 border_width=1, border_color=BORDE)
        abierto = False

        def alternar():
            nonlocal abierto
            abierto = not abierto
            if abierto:
                contenido.pack(fill="x", padx=(2, 8), pady=(0, 7), after=boton)
            else:
                contenido.pack_forget()
            boton.configure(text=("▾  " if abierto else "▸  ") + titulo)

        boton.configure(command=alternar)
        interior = ctk.CTkFrame(contenido, fg_color="transparent")
        interior.pack(fill="x", padx=22, pady=16)
        return interior

    def crear_instalacion(self, panel):
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self._cabecera(scroll, "PASO 01 / 03", "Datos de la instalación",
                       "Describe el recorrido del agua. Las dos alturas representan el tanque al inicio y cerca del final.")
        aviso = ctk.CTkFrame(scroll, fg_color="#fff5df", corner_radius=10)
        aviso.pack(fill="x", padx=(2, 8), pady=(0, 8))
        self.aviso_ejemplo = ctk.CTkLabel(aviso, text="", text_color="#85551b",
                                          anchor="w", justify="left", wraplength=760)
        self.aviso_ejemplo.pack(fill="x", padx=14, pady=10)

        tuberia = self._seccion(scroll, "01", "Recorrido de la tubería",
                                "Ingresa la distancia real que recorrerá el agua a lo largo del tubo, no solo la distancia en línea recta.")
        rejilla = self._rejilla(tuberia)
        self._campo(rejilla, "longitud", "Distancia del recorrido  ·  m", 0, 0)
        self._campo(rejilla, "diametro", "Diámetro interior  ·  mm", 0, 1)
        self._opcion(rejilla, "material", "Material", list(MATERIALES), 1, 0, 2)
        self._nota(tuberia, "El material selecciona un coeficiente de fricción aproximado; no describe el estado particular de tu tubo.")

        niveles = self._seccion(scroll, "02", "Niveles del agua", "Mide desde la superficie de la fuente hasta la del tanque en cada condición.")
        rejilla = self._rejilla(niveles)
        self._campo(rejilla, "desnivel_vacio", "Tanque casi vacío  ·  m", 0, 0)
        self._campo(rejilla, "desnivel_lleno", "Tanque casi lleno  ·  m", 0, 1)
        self._nota(niveles, "Si también baja el nivel de la fuente, inclúyelo en el desnivel de cada condición.")

        accesorios = self._seccion(scroll, "03", "Accesorios", "Indica cuántas piezas de cada tipo hay en el recorrido.")
        rejilla = self._rejilla(accesorios, 3)
        for indice, nombre in enumerate(ACCESORIOS):
            self._campo(rejilla, f"accesorio_{indice}", nombre, 0, indice)
        self._nota(accesorios, "Sus coeficientes de pérdida son valores orientativos incorporados al modelo.")

        extra = self._plegable(scroll, "Contexto adicional  ·  opcional")
        rejilla = self._rejilla(extra)
        self._opcion(rejilla, "posicion", "Bomba frente al nivel mínimo de la fuente",
                     ["No indicada", "Por encima", "Al nivel o por debajo"], 0, 0, 2)
        origen = ["No indicado", "Medido", "Ficha", "Supuesto", "Demostración"]
        self._opcion(rejilla, "origen_tuberia", "Origen de tubería y accesorios", origen, 1, 0)
        self._opcion(rejilla, "origen_niveles", "Origen de los desniveles", origen, 1, 1)
        self._nota(extra, "La posición de la bomba solo destaca una advertencia: PumpCalc no verifica la succión.")

    def crear_bomba(self, panel):
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self._cabecera(scroll, "PASO 02 / 03", "Curva de la bomba",
                       "Cada fila relaciona un caudal con la altura que entrega la bomba. Usa puntos de una misma curva.")
        curva = self._seccion(scroll, "01", "Puntos caudal–altura",
                             "Ordena de menor a mayor caudal. La altura debe disminuir o mantenerse.")
        rejilla = self._rejilla(curva)
        self._opcion(rejilla, "unidad", "Unidad del caudal", list(UNIDADES), 0, 0)
        self._nota(curva, "Si una ficha solo dice «GPM», confirma que son galones estadounidenses antes de convertirlos.")

        encabezado = ctk.CTkFrame(curva, fg_color="#eef4f7", corner_radius=8)
        encabezado.pack(fill="x", pady=(14, 2))
        encabezado.grid_columnconfigure((1, 2), weight=1)
        ctk.CTkLabel(encabezado, text="#", text_color=SECUNDARIO, width=38).grid(row=0, column=0, padx=8, pady=7)
        self.etiqueta_unidad = ctk.CTkLabel(encabezado, text="Caudal (m³/h)", text_color=TEXTO, anchor="w")
        self.etiqueta_unidad.grid(row=0, column=1, sticky="ew", padx=6)
        ctk.CTkLabel(encabezado, text="Altura (m)", text_color=TEXTO, anchor="w").grid(row=0, column=2, sticky="ew", padx=6)
        ctk.CTkLabel(encabezado, text="", width=50).grid(row=0, column=3)
        self.variables["unidad"].trace_add("write", lambda *_: self.etiqueta_unidad.configure(
            text=f"Caudal ({self.variables['unidad'].get()})"))

        self.contenedor_filas = ctk.CTkFrame(curva, fg_color="transparent")
        self.contenedor_filas.pack(fill="x")
        ctk.CTkButton(curva, text="+ Añadir punto", height=34, width=145,
                      fg_color="#e8f0f4", hover_color="#d9e7ed", text_color=TEXTO,
                      command=self.agregar_punto).pack(anchor="w", pady=(10, 0))
        self._nota(curva, "Se requieren al menos dos puntos. El cálculo interpola entre ellos y no prolonga la curva fuera de ese intervalo.")
        self.agregar_punto()
        self.agregar_punto()

        extra = self._plegable(scroll, "Identificación de la curva  ·  opcional")
        rejilla = self._rejilla(extra)
        self._campo(rejilla, "fabricante", "Fabricante de la bomba", 0, 0)
        self._campo(rejilla, "modelo", "Modelo", 0, 1)
        self._campo(rejilla, "condicion_bomba", "Condición de operación", 1, 0)
        self._campo(rejilla, "referencia", "Referencia de la curva", 1, 1,
                    placeholder="Ej.: ficha del fabricante")
        self._opcion(rejilla, "origen_curva", "Origen de los puntos",
                     ["No indicado", "Ficha", "Medido", "Supuesto", "Demostración"], 2, 0, 2)
        self._nota(extra, "Estos datos ayudan a reconocer la curva, pero no cambian la operación matemática.")

    def agregar_punto(self, caudal="", altura=""):
        if self.contenedor_filas is None:
            return
        fila = ctk.CTkFrame(self.contenedor_filas, fg_color="transparent")
        fila.pack(fill="x", pady=3)
        fila.grid_columnconfigure((1, 2), weight=1, uniform="punto")
        numero = ctk.CTkLabel(fila, text="", text_color=SECUNDARIO, width=38)
        numero.grid(row=0, column=0, padx=8)
        q_var = tk.StringVar(value=caudal)
        h_var = tk.StringVar(value=altura)
        q_var.trace_add("write", lambda *_: self.al_cambiar())
        h_var.trace_add("write", lambda *_: self.al_cambiar())
        q = ctk.CTkEntry(fila, textvariable=q_var, height=36, border_color="#cbd8e0")
        h = ctk.CTkEntry(fila, textvariable=h_var, height=36, border_color="#cbd8e0")
        q.grid(row=0, column=1, sticky="ew", padx=6)
        h.grid(row=0, column=2, sticky="ew", padx=6)
        quitar = ctk.CTkButton(fila, text="×", width=38, height=34,
                               fg_color="#eef4f7", text_color="#80505a",
                               hover_color="#f5dfe1")
        quitar.grid(row=0, column=3, padx=6)
        registro = {"frame": fila, "numero": numero, "q": q_var, "h": h_var,
                    "entrada_q": q}
        quitar.configure(command=lambda: self.quitar_punto(registro))
        self.filas_curva.append(registro)
        self._renumerar()
        self.al_cambiar()

    def quitar_punto(self, registro):
        if len(self.filas_curva) <= 2:
            return
        self.filas_curva.remove(registro)
        registro["frame"].destroy()
        self._renumerar()
        self.al_cambiar()

    def _renumerar(self):
        for indice, registro in enumerate(self.filas_curva, 1):
            registro["numero"].configure(text=f"{indice:02d}")
        if self.filas_curva:
            self.controles["puntos"] = self.filas_curva[0]["entrada_q"]

    def datos(self):
        datos = {clave: variable.get() for clave, variable in self.variables.items()}
        datos["puntos"] = "\n".join(
            f"{fila['q'].get().strip()}; {fila['h'].get().strip()}"
            for fila in self.filas_curva if fila["q"].get().strip() or fila["h"].get().strip()
        )
        return datos

    def cargar(self, datos):
        for clave, variable in self.variables.items():
            variable.set(datos.get(clave, self.valores_iniciales[clave]))
        for registro in self.filas_curva:
            registro["frame"].destroy()
        self.filas_curva.clear()
        lineas = [linea for linea in datos.get("puntos", "").splitlines() if linea.strip()]
        for linea in lineas:
            partes = linea.split(";", 1)
            self.agregar_punto(partes[0].strip(), partes[1].strip() if len(partes) > 1 else "")
        while len(self.filas_curva) < 2:
            self.agregar_punto()

    def actualizar_aviso(self):
        if self.aviso_ejemplo is None:
            return
        es_demo = any(self.variables.get(clave) is not None and
                      self.variables[clave].get() == "Demostración" for clave in
                      ("origen_tuberia", "origen_niveles", "origen_curva"))
        self.aviso_ejemplo.configure(text=(
            "EJEMPLO CARGADO  ·  Estos valores ilustran el cálculo; reemplázalos por los de tu instalación."
            if es_demo else
            "DATOS DE LA INSTALACIÓN  ·  Revisa que las medidas y la curva correspondan al mismo caso."
        ))
