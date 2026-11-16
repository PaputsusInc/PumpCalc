"""Ventana principal: captura, resultados y escenarios locales."""

import tkinter as tk
from tkinter import messagebox
import sqlite3

import customtkinter as ctk

from pumpcalc.casos_uso import ACCESORIOS, ErrorEntrada, calcular_escenario, firma_calculo
from pumpcalc.persistencia import AlmacenEscenarios
from pumpcalc.ui.formulario import Formulario
from pumpcalc.ui.grafica import dibujar


DEMOSTRACION = {
    "longitud": "40", "diametro": "32", "material": "PVC",
    "desnivel_vacio": "12", "desnivel_lleno": "12",
    "accesorio_0": "2", "accesorio_1": "1", "accesorio_2": "1",
    "posicion": "No indicada", "origen_tuberia": "Demostración",
    "origen_niveles": "Demostración", "origen_curva": "Demostración",
    "fabricante": "", "modelo": "Curva de demostración",
    "condicion_bomba": "Ejemplo académico", "referencia": "",
    "unidad": "m³/h", "puntos": "0; 38\n2; 35\n4; 29\n6; 19\n8; 5",
}


class PumpCalcApp(ctk.CTk):
    """Coordina el formulario de escritorio, el cálculo y los casos guardados."""

    def __init__(self, almacen=None):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.title("PumpCalc")
        self.geometry("1180x830")
        self.minsize(950, 690)
        self.configure(fg_color="#f3f7fb")
        self.almacen = almacen or AlmacenEscenarios()
        self.escenario_id = None
        self.calculo = None
        self.firma = None
        self._cargando = False
        self.formulario = Formulario(self._cambio)
        self.variables = self.formulario.variables
        self.controles = self.formulario.controles
        self.paneles = {}
        self.botones = {}
        self.panel_actual = "Instalación"
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._menu()
        self._contenido()
        self._aplicar_entradas(DEMOSTRACION)
        self.nombre_var.set("")
        self._mostrar_panel("Instalación")
        self._mostrar_espacio("Cálculo")
        self._refrescar_resultados()

    def _menu(self):
        menu = ctk.CTkFrame(self, width=205, corner_radius=0, fg_color="#10243a")
        menu.grid(row=0, column=0, sticky="nsew")
        menu.grid_propagate(False)
        ctk.CTkLabel(menu, text="PumpCalc", text_color="white",
                     font=ctk.CTkFont(size=25, weight="bold")).pack(anchor="w", padx=18, pady=(30, 4))
        ctk.CTkLabel(menu, text="Una bomba · una línea", text_color="#a9bed1").pack(anchor="w", padx=18, pady=(0, 26))
        for grupo, nombres in (("PREPARAR", ("Instalación", "Curva de bomba")),
                               ("ANALIZAR", ("Resultados", "Escenarios"))):
            ctk.CTkLabel(menu, text=grupo, text_color="#83a6ba", anchor="w",
                         font=ctk.CTkFont(size=11, weight="bold")).pack(fill="x", padx=20, pady=(10, 7))
            for nombre in nombres:
                boton = ctk.CTkButton(menu, text=nombre, anchor="w", height=42,
                                      fg_color="transparent", hover_color="#1d3c5b",
                                      command=lambda n=nombre: self._mostrar_panel(n) if n != "Escenarios"
                                      else self._mostrar_espacio("Escenarios"))
                boton.pack(fill="x", padx=12, pady=3)
                self.botones[nombre] = boton
        ctk.CTkLabel(menu, text="Estimación académica\nSucción no evaluada",
                     text_color="#b7c9d7", justify="left").pack(side="bottom", anchor="w", padx=18, pady=22)

    def _contenido(self):
        self.contenedor = ctk.CTkFrame(self, fg_color="transparent")
        self.contenedor.grid(row=0, column=1, sticky="nsew", padx=20, pady=16)
        self.contenedor.grid_columnconfigure(0, weight=1)
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.vista_calculo = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        self.vista_escenarios = ctk.CTkFrame(self.contenedor, fg_color="transparent")
        for vista in (self.vista_calculo, self.vista_escenarios):
            vista.grid(row=0, column=0, sticky="nsew")
        self._vista_calculo()
        self._vista_escenarios()

    def _vista_calculo(self):
        vista = self.vista_calculo
        vista.grid_columnconfigure(0, weight=1)
        vista.grid_rowconfigure(2, weight=1)
        encabezado = ctk.CTkFrame(vista, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew")
        encabezado.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(encabezado, text="Evaluación de la bomba", font=ctk.CTkFont(size=27, weight="bold"),
                     text_color="#142b40").grid(row=0, column=0, sticky="w")
        ctk.CTkButton(encabezado, text="¿Qué datos necesito?", width=160,
                      fg_color="#dce8ef", text_color="#17374c",
                      command=self._mostrar_ayuda).grid(row=0, column=1, sticky="e")
        self.nombre_var = tk.StringVar()
        acciones = ctk.CTkFrame(encabezado, fg_color="transparent")
        acciones.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))
        ctk.CTkLabel(acciones, text="Escenario", text_color="#557083",
                     font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
        ctk.CTkEntry(acciones, textvariable=self.nombre_var, width=260,
                     placeholder_text="Ponle un nombre para guardarlo").pack(side="left", padx=(0, 8))
        ctk.CTkButton(acciones, text="Guardar", width=90,
                      command=self._guardar).pack(side="left")
        self.aviso = ctk.CTkLabel(vista, text="", text_color="#a13c2a", anchor="w", justify="left")
        self.aviso.grid(row=1, column=0, sticky="ew", pady=(5, 3))
        cuerpo = ctk.CTkFrame(vista, fg_color="transparent")
        cuerpo.grid(row=2, column=0, sticky="nsew")
        cuerpo.grid_columnconfigure(0, weight=1)
        cuerpo.grid_rowconfigure(0, weight=1)
        for nombre in ("Instalación", "Curva de bomba", "Resultados"):
            panel = ctk.CTkFrame(cuerpo, fg_color="transparent")
            panel.grid(row=0, column=0, sticky="nsew")
            self.paneles[nombre] = panel
        self.formulario.crear_instalacion(self.paneles["Instalación"])
        self.formulario.crear_bomba(self.paneles["Curva de bomba"])
        self._panel_resultados(self.paneles["Resultados"])
        pie = ctk.CTkFrame(vista, fg_color="transparent")
        pie.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ctk.CTkButton(pie, text="Calcular ambas condiciones", height=43,
                      fg_color="#198d77", command=self._calcular).pack(side="right")

    def _titulo(self, parent, titulo, descripcion):
        ctk.CTkLabel(parent, text=titulo, font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#17374c", anchor="w").pack(fill="x", pady=(4, 2))
        ctk.CTkLabel(parent, text=descripcion, text_color="#557083", anchor="w",
                     justify="left", wraplength=780).pack(fill="x", pady=(0, 14))

    def _panel_resultados(self, panel):
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        self._titulo(scroll, "Resultados", "Caudales estimados para las dos condiciones del tanque.")
        self.estado_resultado = ctk.CTkLabel(scroll, text="", text_color="#a45b12", anchor="w",
                                              font=ctk.CTkFont(weight="bold"))
        self.estado_resultado.pack(fill="x")
        self.resumen = ctk.CTkLabel(scroll, text="", anchor="w", justify="left", wraplength=790,
                                    font=ctk.CTkFont(size=17, weight="bold"), text_color="#153d56")
        self.resumen.pack(fill="x", pady=(4, 12))
        self.detalles = {}
        for clave, titulo in (("vacio", "Tanque casi vacío"), ("lleno", "Tanque casi lleno")):
            caja = ctk.CTkFrame(scroll, fg_color="white", corner_radius=12)
            caja.pack(fill="x", pady=5)
            ctk.CTkLabel(caja, text=titulo, font=ctk.CTkFont(size=16, weight="bold"),
                         text_color="#17374c").pack(anchor="w", padx=15, pady=(12, 2))
            etiqueta = ctk.CTkLabel(caja, text="", anchor="w", justify="left", wraplength=770,
                                     text_color="#334e60")
            etiqueta.pack(fill="x", padx=15, pady=(0, 12))
            self.detalles[clave] = etiqueta
        self.succion = ctk.CTkLabel(scroll, text="", anchor="w", justify="left", wraplength=790,
                                    text_color="#a45b12")
        self.succion.pack(fill="x", pady=10)
        self.grafica = tk.Canvas(scroll, bg="white", height=330, highlightthickness=0)
        self.grafica.pack(fill="x", pady=8)
        self.grafica.bind("<Configure>", lambda _e: dibujar(self.grafica, self.calculo))
        ctk.CTkLabel(scroll, text="Curva interpolada entre los puntos ingresados; C y K son aproximados. Los dos caudales no predicen el tiempo total de llenado.",
                     anchor="w", justify="left", wraplength=790, text_color="#607688").pack(fill="x", pady=8)

    def _vista_escenarios(self):
        vista = self.vista_escenarios
        ctk.CTkLabel(vista, text="Escenarios guardados", font=ctk.CTkFont(size=27, weight="bold"),
                     text_color="#142b40").pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(vista, text="Guarda borradores, abre configuraciones y duplica alternativas independientes.",
                     text_color="#557083").pack(anchor="w", pady=(0, 10))
        self.lista_escenarios = ctk.CTkScrollableFrame(vista, height=260, fg_color="white")
        self.lista_escenarios.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(vista, text="Comparar dos escenarios guardados", text_color="#17374c",
                     font=ctk.CTkFont(size=17, weight="bold")).pack(anchor="w")
        fila = ctk.CTkFrame(vista, fg_color="transparent")
        fila.pack(fill="x", pady=7)
        self.selector_a = ctk.CTkOptionMenu(fila, values=["—"], width=280)
        self.selector_a.pack(side="left", padx=(0, 8))
        self.selector_b = ctk.CTkOptionMenu(fila, values=["—"], width=280)
        self.selector_b.pack(side="left", padx=(0, 8))
        ctk.CTkButton(fila, text="Comparar", width=100, command=self._comparar).pack(side="left")
        self.texto_comparacion = ctk.CTkTextbox(vista, height=230)
        self.texto_comparacion.pack(fill="both", expand=True)
        self.texto_comparacion.configure(state="disabled")

    def _mostrar_espacio(self, nombre):
        if nombre == "Escenarios":
            self.vista_escenarios.tkraise()
            self._resaltar_navegacion("Escenarios")
            self._refrescar_escenarios()
        else:
            self.vista_calculo.tkraise()
            self._resaltar_navegacion(self.panel_actual)

    def _resaltar_navegacion(self, activo):
        for nombre, boton in self.botones.items():
            boton.configure(fg_color="#1b4966" if nombre == activo else "transparent")

    def _mostrar_ayuda(self):
        messagebox.showinfo(
            "¿Qué datos necesito?",
            "PumpCalc estima el caudal de una bomba hacia un tanque abierto mediante una sola tubería.\n\n"
            "De la finca: distancia a lo largo del tubo, diámetro interior, material, accesorios y "
            "desnivel entre superficies de agua con el tanque casi vacío y casi lleno. Puedes medirlos o "
            "consultar el plano y la especificación del tubo. No necesitas conocer de antemano el caudal "
            "ni la velocidad del agua.\n\n"
            "De la bomba: al menos dos pares caudal–altura de una misma curva. "
            "Comprueba si la unidad es m³/h, L/min o galón estadounidense por minuto.\n\n"
            "Si conoces el fabricante, modelo o referencia, puedes anotarlos para identificar la curva. "
            "No son necesarios para hacer la operación matemática.\n\n"
            "Los valores precargados son una demostración. El cálculo no verifica la succión, potencia ni "
            "tiempo total de llenado.",
            parent=self,
        )

    def _mostrar_panel(self, nombre):
        self.vista_calculo.tkraise()
        self.paneles[nombre].tkraise()
        self.panel_actual = nombre
        self._resaltar_navegacion(nombre)

    def _datos_actuales(self):
        return self.formulario.datos()

    def _aplicar_entradas(self, datos):
        self._cargando = True
        try:
            self.formulario.cargar(datos)
        finally:
            self._cargando = False
        self.formulario.actualizar_aviso()

    def _cambio(self):
        if not self._cargando:
            self.formulario.actualizar_aviso()
        if not self._cargando and hasattr(self, "estado_resultado"):
            self._refrescar_resultados()

    def _vigente(self):
        """Comprueba si el resultado corresponde a las entradas actuales."""
        return self.calculo is not None and self.firma == firma_calculo(self._datos_actuales())

    def _refrescar_resultados(self):
        if self.calculo is None:
            self.estado_resultado.configure(text="Sin calcular / borrador")
            self.resumen.configure(text="Completa los datos y pulsa Calcular.")
            for etiqueta in self.detalles.values():
                etiqueta.configure(text="Todavía no hay un resultado para esta condición.")
        else:
            vigente = self._vigente()
            self.estado_resultado.configure(text="Resultado vigente" if vigente else "DESACTUALIZADO: los datos cambiaron; recalcula antes de interpretarlo.")
            self.resumen.configure(text=self.calculo["resumen"])
            for clave in ("vacio", "lleno"):
                condicion = self.calculo["condiciones"][clave]
                r = condicion["resultado"]
                if r:
                    texto = (f"Caudal: {r['caudal_m3h']:.3f} m³/h · Altura: {r['total_m']:.2f} m · "
                             f"Velocidad: {r['velocidad_ms']:.2f} m/s\n"
                             f"Pérdida en tubería: {r['tuberia_m']:.2f} m · "
                             f"Accesorios: {r['accesorios_m']:.2f} m\n{condicion['mensaje']}")
                else:
                    texto = f"Sin caudal calculado. {condicion['mensaje']}"
                self.detalles[clave].configure(text=texto)
        posicion = self.variables["posicion"].get()
        aviso = "Succión no evaluada: el caudal estimado no garantiza el funcionamiento de la bomba."
        if posicion == "Por encima":
            aviso += " ATENCIÓN: la bomba está por encima del nivel mínimo de la fuente."
        self.succion.configure(text=aviso)
        dibujar(self.grafica, self.calculo)

    def _calcular(self):
        datos = self._datos_actuales()
        try:
            calculo = calcular_escenario(datos)
        except ErrorEntrada as error:
            self.aviso.configure(text=str(error))
            self._mostrar_panel("Curva de bomba" if error.campo in
                                ("unidad", "puntos")
                                else "Instalación")
            self.controles[error.campo].focus_set()
            return
        self.calculo = calculo
        self.firma = firma_calculo(datos)
        self.aviso.configure(text="")
        self._refrescar_resultados()
        self._mostrar_panel("Resultados")

    def _guardar(self):
        nombre = self.nombre_var.get().strip()
        if not nombre:
            self.aviso.configure(text="Escribe un nombre descriptivo para guardar el escenario.")
            return
        escenario = {"id": self.escenario_id, "nombre": nombre,
                     "entradas": self._datos_actuales(), "calculo": self.calculo, "firma": self.firma}
        try:
            self.escenario_id = self.almacen.guardar(escenario)
        except (OSError, sqlite3.Error) as error:
            self.aviso.configure(text=f"No se pudo guardar: {error}")
            return
        self.aviso.configure(text=f"Escenario «{nombre}» guardado localmente.")

    def _refrescar_escenarios(self):
        for hijo in self.lista_escenarios.winfo_children():
            hijo.destroy()
        try:
            escenarios = self.almacen.listar()
        except (OSError, ValueError, sqlite3.Error):
            escenarios = []
        self._opciones_escenario = {}
        if not escenarios:
            ctk.CTkLabel(self.lista_escenarios, text="Aún no hay escenarios guardados.").pack(anchor="w", padx=12, pady=12)
        for escenario in escenarios:
            fila = ctk.CTkFrame(self.lista_escenarios, fg_color="#f4f8fb")
            fila.pack(fill="x", padx=8, pady=5)
            estado = "borrador" if not escenario["calculo"] else (
                "vigente" if escenario["firma"] == firma_calculo(escenario["entradas"]) else "desactualizado")
            ctk.CTkLabel(fila, text=f"{escenario['nombre']}  ·  {estado}  ·  {escenario['actualizado'][:16]}",
                         anchor="w", text_color="#263f52").pack(side="left", fill="x", expand=True, padx=10)
            ctk.CTkButton(fila, text="Abrir", width=64,
                          command=lambda e=escenario: self._abrir(e)).pack(side="right", padx=4)
            ctk.CTkButton(fila, text="Duplicar", width=76,
                          command=lambda e=escenario: self._duplicar(e)).pack(side="right", padx=4)
            etiqueta = f"{escenario['nombre']} [{escenario['id'][:8]}]"
            self._opciones_escenario[etiqueta] = escenario
        opciones = list(self._opciones_escenario) or ["—"]
        self.selector_a.configure(values=opciones)
        self.selector_b.configure(values=opciones)
        self.selector_a.set(opciones[0])
        self.selector_b.set(opciones[1] if len(opciones) > 1 else opciones[0])

    def _abrir(self, escenario):
        self.escenario_id = escenario["id"]
        self.nombre_var.set(escenario["nombre"])
        self.calculo = escenario["calculo"]
        self.firma = escenario["firma"]
        self._aplicar_entradas(escenario["entradas"])
        self.aviso.configure(text="")
        self._refrescar_resultados()
        self._mostrar_espacio("Cálculo")
        self._mostrar_panel("Resultados" if self.calculo else "Instalación")

    def _duplicar(self, escenario):
        self._abrir(escenario)
        self.escenario_id = None
        self.nombre_var.set(escenario["nombre"] + " · copia")
        self.firma = None  # la copia necesita un cálculo propio antes de comparar
        self._refrescar_resultados()
        self.aviso.configure(text="Copia independiente. Cambia datos, recalcula y guarda con un nombre nuevo.")

    def _comparar(self):
        a = self._opciones_escenario.get(self.selector_a.get())
        b = self._opciones_escenario.get(self.selector_b.get())
        if not a or not b or a["id"] == b["id"]:
            texto = "Selecciona dos escenarios distintos."
        else:
            claves = (("longitud", "Distancia del recorrido (m)"),
                      ("diametro", "Diámetro interior (mm)"), ("material", "Material"),
                      ("desnivel_vacio", "Desnivel inicial (m)"),
                      ("desnivel_lleno", "Desnivel final (m)"),
                      ("modelo", "Modelo"), ("unidad", "Unidad de curva"),
                      ("puntos", "Curva"))
            lineas = [f"{a['nombre']}  ↔  {b['nombre']}", "", "Entradas diferentes:"]
            cambios = 0
            for clave, titulo in claves:
                va, vb = a["entradas"].get(clave, ""), b["entradas"].get(clave, "")
                if va != vb:
                    lineas.append(f"{titulo}: {va}  →  {vb}")
                    cambios += 1
            for i, nombre in enumerate(ACCESORIOS):
                clave = f"accesorio_{i}"
                va, vb = a["entradas"].get(clave, ""), b["entradas"].get(clave, "")
                if va != vb:
                    lineas.append(f"{nombre}: {va}  →  {vb}")
                    cambios += 1
            if not cambios:
                lineas.append("No hay cambios en las entradas principales.")
            for escenario in (a, b):
                lineas.extend(["", escenario["nombre"] + ":"])
                if not escenario["calculo"]:
                    lineas.append("Borrador sin resultados.")
                    continue
                if escenario["firma"] != firma_calculo(escenario["entradas"]):
                    lineas.append("Resultados desactualizados; recalcula antes de compararlos.")
                    continue
                for clave, titulo in (("vacio", "Tanque casi vacío"), ("lleno", "Tanque casi lleno")):
                    r = escenario["calculo"]["condiciones"][clave]["resultado"]
                    lineas.append(f"{titulo}: {r['caudal_m3h']:.3f} m³/h" if r else f"{titulo}: sin cruce en curva")
            texto = "\n".join(lineas)
        self.texto_comparacion.configure(state="normal")
        self.texto_comparacion.delete("1.0", "end")
        self.texto_comparacion.insert("1.0", texto)
        self.texto_comparacion.configure(state="disabled")
