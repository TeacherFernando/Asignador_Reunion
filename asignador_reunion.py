import tkinter as tk
from tkinter import messagebox, ttk, PhotoImage  # Asegúrate de incluir PhotoImage aquí
import json
import random
import os
from datetime import datetime


# Verificar si el archivo JSON existe, si no, crear uno con datos de ejemplo
def cargar_participantes():
    try:
        with open("participantes.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        participantes = [
            {"nombre": "Juan Miranda Llanos", "sexo": "Masculino", "categoria": "Anciano", "edad": "adulto"},
            {"nombre": "Maria Gonzalez", "sexo": "Femenino", "categoria": "Publicador Fuerte", "edad": "adulto"},
            {"nombre": "Pedro Jimenez", "sexo": "Masculino", "categoria": "Acompañante", "edad": "niño"},
        ]
        with open("participantes.json", "w") as file:
            json.dump(participantes, file, indent=4)
        return participantes

# Cargar historial de asignaciones
def cargar_historial():
    try:
        with open("historial.json", "r") as file:
            historial = json.load(file)
            # Convertir formato antiguo (número de participaciones) al nuevo (lista de fechas)
            for nombre, participaciones in historial.items():
                if isinstance(participaciones, int):  # Formato antiguo
                    historial[nombre] = []  # Inicializar con una lista vacía
            return historial
    except FileNotFoundError:
        return {}

# Reglas de elegibilidad con la nueva estructura
def reglas_elegibilidad(asignacion, participante):
    if participante["categoria"] == "Acompañante":
        return False  # Los acompañantes no pueden ser titulares
    if asignacion in ["Haga discípulos", "Explique sus creencias"]:
        return participante["categoria"] == "Publicador Fuerte"  # Solo publicadores fuertes como titulares
    if asignacion == "Presidente":
        return participante["categoria"] == "Anciano Power"
    elif asignacion == "Oración de inicio":
        return participante["sexo"] == "Masculino" and participante["categoria"] in ["Publicador Fuerte", "Siervo Ministerial", "Anciano"]
    elif asignacion == "Tesoros de la Biblia":
        return participante["categoria"] in ["Anciano", "Siervo Ministerial Power"]
    elif asignacion == "Busquemos perlas escondidas":
        return participante["categoria"] in ["Anciano", "Siervo Ministerial Power", "Siervo Ministerial"]
    elif asignacion == "Lectura de la Biblia":
        return participante["sexo"] == "Masculino" and participante["categoria"] in ["Publicador Fuerte", "Publicador Débil"]
    elif asignacion == "Lo que hizo Jesús" or asignacion == "Imite a Jesús":
        return participante["categoria"] in ["Anciano", "Anciano Power"]
    elif asignacion in ["Empiece conversaciones", "Haga revisitas"]:
        if participante["edad"] == "niño":
            return True  # Los niños solo pueden ser titulares
        return participante["categoria"] in ["Publicador Fuerte", "Publicador Débil"]
    elif asignacion == "Discurso":
        return participante["sexo"] == "Masculino" and participante["categoria"] in ["Publicador Fuerte", "Siervo Ministerial"]
    elif asignacion == "Análisis":
        return participante["categoria"] in ["Anciano", "Siervo Ministerial Power", "Anciano Power"]
    elif asignacion == "Necesidades de la congregación":
        return participante["categoria"] == "Anciano Power"
    elif asignacion == "Estudio bíblico de la congregación":
        return participante["categoria"] in ["Anciano", "Anciano Power"]
    elif asignacion == "Lector":
        return participante["sexo"] == "Masculino" and participante["categoria"] in ["Siervo Ministerial Power", "Publicador Fuerte"]
    elif asignacion == "Oración final":
        return participante["sexo"] == "Masculino" and participante["categoria"] in ["Publicador Fuerte", "Siervo Ministerial", "Siervo Ministerial Power"]
    elif asignacion == "Acomodador":
        return participante["sexo"] == "Masculino" and participante["categoria"] in ["Publicador Fuerte", "Siervo Ministerial"]
    return False

# Función para asignar participantes al programa
def asignar_participantes(programa, participantes):
    historial = cargar_historial()
    asignaciones = {}
    asignados_dia = set()  # Seguimiento de participantes ya asignados en el día

    # Definir partes prioritarias
    partes_prioritarias = ["Presidente", "Necesidades de la congregación"]

    # Partes que requieren titular y acompañante
    partes_con_acompanante = ["Empiece conversaciones", "Haga revisitas", "Haga discípulos", "Explique sus creencias"]

    # Asignar partes prioritarias primero
    for parte_id in programa:
        parte_base = parte_id.split(" (")[0]  # Obtener el nombre base de la parte
        if parte_base in partes_prioritarias:
            posibles = [p for p in participantes if reglas_elegibilidad(parte_base, p) and p["nombre"] not in asignados_dia]
            posibles.sort(key=lambda p: min(
                (fecha_asignacion["fecha"] for fecha_asignacion in historial.get(p["nombre"], []) if fecha_asignacion["asignacion"] == parte_base),
                default="1970-01-01"
            ))  # Priorizar por fecha más antigua de esa asignación

            if posibles:
                asignado = posibles[0]
                asignaciones[parte_id] = asignado["nombre"]
                asignados_dia.add(asignado["nombre"])  # Marcar como asignado

                # Actualizar historial
                historial.setdefault(asignado["nombre"], []).append({
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                    "asignacion": parte_base
                })
            else:
                asignaciones[parte_id] = "Sin opciones válidas"

    # Asignar las demás partes
    for parte_id in programa:
        parte_base = parte_id.split(" (")[0]  # Obtener el nombre base de la parte
        if parte_base not in partes_prioritarias:
            if parte_base in partes_con_acompanante:
                # Filtrar posibles titulares
                posibles_titulares = [p for p in participantes if reglas_elegibilidad(parte_base, p) and p["nombre"] not in asignados_dia]
                posibles_titulares.sort(key=lambda p: min(
                    (fecha_asignacion["fecha"] for fecha_asignacion in historial.get(p["nombre"], []) if fecha_asignacion["asignacion"] == parte_base),
                    default="1970-01-01"
                ))  # Priorizar por fecha más antigua de esa asignación

                if posibles_titulares:
                    titular = posibles_titulares[0]
                    asignados_dia.add(titular["nombre"])  # Marcar titular como asignado

                    # Filtrar posibles acompañantes
                    posibles_acompanantes = [
                        p for p in participantes
                        if p["nombre"] != titular["nombre"]  # No puede ser el titular
                        and p["nombre"] not in asignados_dia  # No puede estar ya asignado
                        and p["categoria"] == "Acompañante"  # Debe ser acompañante
                    ]
                    posibles_acompanantes.sort(key=lambda p: min(
                        (fecha_asignacion["fecha"] for fecha_asignacion in historial.get(p["nombre"], []) if fecha_asignacion["asignacion"] == parte_base),
                        default="1970-01-01"
                    ))  # Priorizar por fecha más antigua de esa asignación

                    if posibles_acompanantes:
                        acompanante = posibles_acompanantes[0]
                        asignados_dia.add(acompanante["nombre"])  # Marcar acompañante como asignado

                        # Guardar la asignación con titular y acompañante
                        asignaciones[parte_id] = {
                            "titular": titular["nombre"],
                            "acompanante": acompanante["nombre"]
                        }

                        # Actualizar historial
                        historial.setdefault(titular["nombre"], []).append({
                            "fecha": datetime.now().strftime("%Y-%m-%d"),
                            "asignacion": parte_base
                        })
                        historial.setdefault(acompanante["nombre"], []).append({
                            "fecha": datetime.now().strftime("%Y-%m-%d"),
                            "asignacion": parte_base
                        })
                    else:
                        asignaciones[parte_id] = {"titular": titular["nombre"], "acompanante": "Sin opciones válidas"}
                else:
                    asignaciones[parte_id] = {"titular": "Sin opciones válidas", "acompanante": "Sin opciones válidas"}
            else:
                # Asignar partes normales (sin acompañante)
                posibles = [p for p in participantes if reglas_elegibilidad(parte_base, p) and p["nombre"] not in asignados_dia]
                posibles.sort(key=lambda p: min(
                    (fecha_asignacion["fecha"] for fecha_asignacion in historial.get(p["nombre"], []) if fecha_asignacion["asignacion"] == parte_base),
                    default="1970-01-01"
                ))  # Priorizar por fecha más antigua de esa asignación

                if posibles:
                    asignado = posibles[0]
                    asignaciones[parte_id] = asignado["nombre"]
                    asignados_dia.add(asignado["nombre"])  # Marcar como asignado

                    # Actualizar historial
                    historial.setdefault(asignado["nombre"], []).append({
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                        "asignacion": parte_base
                    })
                else:
                    asignaciones[parte_id] = "Sin opciones válidas"

    # Guardar el historial actualizado
    with open("historial.json", "w") as file:
        json.dump(historial, file, indent=4)

    return asignaciones

# Crear la interfaz gráfica


class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Asignador de Reunión")  # Cambiar el título de la ventana
        self.root.geometry("1000x800")  # Aumentar el ancho de la ventana para que se vea el nuevo botón

        # Obtener la ruta absoluta del archivo de ícono
        ruta_icono = os.path.join(os.path.dirname(__file__), "icono.png")

        # Establecer un ícono para la aplicación
        try:
            icono = PhotoImage(file=ruta_icono)
            self.root.wm_iconphoto(True, icono)
        except Exception as e:
            print(f"No se pudo cargar el ícono: {e}")
            print(f"Ruta del ícono: {ruta_icono}")

        self.participantes = cargar_participantes()
        self.programa = [
            "Presidente", "Oración de inicio", "Tesoros de la Biblia", "Busquemos perlas escondidas", 
            "Lectura de la Biblia", "Lo que hizo Jesús", "Imite a Jesús", "Empiece conversaciones", 
            "Haga revisitas", "Haga discípulos", "Explique sus creencias", "Discurso", "Análisis", 
            "Necesidades de la congregación", "Estudio bíblico de la congregación", "Lector", "Oración final",
            "Acomodador"  # Nueva asignación agregada al final
        ]

        self.asignaciones = {}

        self.crear_widgets()

    def crear_widgets(self):
        # Crear un marco para organizar los botones principales en la parte superior
        self.frame_botones_superior = tk.Frame(self.root)
        self.frame_botones_superior.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Botón para crear un nuevo programa
        self.boton_nuevo_programa = tk.Button(self.frame_botones_superior, text="Nuevo Programa", command=self.nuevo_programa, bg="red", height=1)
        self.boton_nuevo_programa.pack(side=tk.LEFT, padx=5)

        # Botón para generar el programa
        self.boton_generar = tk.Button(self.frame_botones_superior, text="Generar Programa", command=self.generar_programa, bg="lightblue", height=1)
        self.boton_generar.pack(side=tk.LEFT, padx=5)

        # Botón para guardar el programa
        self.boton_guardar = tk.Button(self.frame_botones_superior, text="Guardar Programa", command=self.guardar_programa, bg="lightgreen", height=1)
        self.boton_guardar.pack(side=tk.LEFT, padx=5)

        # Botón para copiar el programa
        self.boton_copiar = tk.Button(self.frame_botones_superior, text="Copiar Programa", command=self.copiar_programa, bg="yellow", height=1)
        self.boton_copiar.pack(side=tk.LEFT, padx=5)

        # Botón para editar la lista de participantes
        self.boton_editar_participantes = tk.Button(self.frame_botones_superior, text="Editar Participantes", command=self.editar_participantes, bg="orange", height=1)
        self.boton_editar_participantes.pack(side=tk.LEFT, padx=5)

        # Nuevo botón para ver el historial
        self.boton_ver_historial = tk.Button(self.frame_botones_superior, text="Ver Historial", command=self.ver_historial, bg="purple", fg="white", height=1)
        self.boton_ver_historial.pack(side=tk.LEFT, padx=5)

        # Crear un marco para las partes de la reunión
        self.frame_partes = tk.Frame(self.root)
        self.frame_partes.pack(side=tk.LEFT, padx=10, pady=10)

        # Crear botones para agregar cada parte de la reunión con menor tamaño
        for parte in self.programa:
            boton_parte = tk.Button(
                self.frame_partes,
                text=f"Agregar {parte}",
                command=lambda p=parte: self.agregar_parte(p),
                bg="lightgray",
                height=1  # Reducir altura del botón
            )
            boton_parte.pack(fill=tk.X, pady=0)  # Reducir el espacio vertical entre botones

        # Crear un marco para el lienzo y la barra de desplazamiento
        self.frame_lienzo = tk.Frame(self.root)
        self.frame_lienzo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear un lienzo para mostrar las asignaciones
        self.lienzo = tk.Canvas(self.frame_lienzo, bg="white")
        self.lienzo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Crear una barra de desplazamiento horizontal
        self.scroll_x = tk.Scrollbar(self.frame_lienzo, orient=tk.HORIZONTAL, command=self.lienzo.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Crear una barra de desplazamiento vertical
        self.scroll_y = tk.Scrollbar(self.frame_lienzo, orient=tk.VERTICAL, command=self.lienzo.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Vincular las barras de desplazamiento al lienzo
        self.lienzo.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        self.lienzo.bind("<Configure>", lambda e: self.lienzo.configure(scrollregion=self.lienzo.bbox("all")))

        # Hacer que las asignaciones sean movibles
        self.lienzo.bind("<B1-Motion>", self.mover_asignacion)

    def nuevo_programa(self):
        # Preguntar si el usuario desea guardar el programa actual
        if self.asignaciones:  # Si hay asignaciones actuales
            respuesta = messagebox.askyesno("Nuevo Programa", "¿Desea guardar el programa actual?")
            if respuesta:  # Si el usuario elige guardar
                self.guardar_programa()

        # Borrar las asignaciones y limpiar el lienzo
        self.asignaciones = {}
        self.lienzo.delete("all")
        messagebox.showinfo("Nuevo Programa", "Puede comenzar a crear un nuevo programa.")

    def copiar_programa(self):
        # Convertir las asignaciones a un formato de tabla delimitada por tabulaciones
        texto_copiable = "Parte\tAsignación\n"
        for parte, asignado in self.asignaciones.items():
            if isinstance(asignado, dict):  # Si es una demostración con titular y acompañante
                texto_copiable += f"{parte}\tTitular: {asignado['titular']}, Acompañante: {asignado['acompanante']}\n"
            else:  # Si es una asignación normal
                texto_copiable += f"{parte}\t{asignado}\n"

        # Usar tkinter para copiar al portapapeles
        self.root.clipboard_clear()
        self.root.clipboard_append(texto_copiable)
        self.root.update()  # Necesario para que el portapapeles se actualice
        messagebox.showinfo("Copiado", "El programa ha sido copiado al portapapeles. Puedes pegarlo en Excel.")

    def agregar_parte(self, parte):
        # Agregar una nueva parte al lienzo
        x, y = 50, 50 + len(self.lienzo.find_withtag("parte")) * 15  # Reducir el interlineado (antes era 30)
        texto = self.lienzo.create_text(x, y, text=parte, anchor="w", tags=("parte",))
        boton_eliminar = self.lienzo.create_rectangle(x - 20, y - 10, x, y + 10, fill="red", tags=("eliminar",))
        self.lienzo.tag_bind(boton_eliminar, "<Button-1>", lambda e, t=texto: self.eliminar_parte(t))

    def eliminar_parte(self, texto):
        # Eliminar una parte del lienzo
        self.lienzo.delete(texto)

    def mover_asignacion(self, event):
        # Mover una asignación en el lienzo
        item = self.lienzo.find_closest(event.x, event.y)
        self.lienzo.coords(item, event.x, event.y)

    def editar_participantes(self):
        """Abrir una ventana para editar los participantes."""
        # Opciones predefinidas para las listas desplegables
        categorias = ["Anciano Power", "Anciano", "Siervo Ministerial Power", "Siervo Ministerial", "Publicador Fuerte", "Publicador Débil", "Acompañante"]
        sexos = ["Femenino", "Masculino"]
        edades = ["adulto", "niño"]

        ventana_editar = tk.Toplevel(self.root)
        ventana_editar.title("Editar Participantes")
        ventana_editar.geometry("700x400")  # Ajustar tamaño para más espacio horizontal

        # Crear un marco para la lista de participantes
        frame_lista = tk.Frame(ventana_editar)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear un Treeview para mostrar los participantes
        columnas = ("nombre", "sexo", "categoria", "edad")
        tree = ttk.Treeview(frame_lista, columns=columnas, show="headings")
        tree.pack(fill=tk.BOTH, expand=True)

        # Configurar encabezados
        for col in columnas:
            tree.heading(col, text=col.capitalize())

        # Agregar participantes al Treeview
        for participante in self.participantes:
            tree.insert("", tk.END, values=(participante["nombre"], participante["sexo"], participante["categoria"], participante["edad"]))

        # Crear un marco para editar un participante seleccionado
        frame_editar = tk.Frame(ventana_editar)
        frame_editar.pack(fill=tk.X, padx=10, pady=10)

        # Crear etiquetas y campos de entrada
        tk.Label(frame_editar, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entrada_nombre = tk.Entry(frame_editar)
        entrada_nombre.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_editar, text="Sexo:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        combobox_sexo = ttk.Combobox(frame_editar, values=sexos, state="readonly")
        combobox_sexo.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame_editar, text="Categoría:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        combobox_categoria = ttk.Combobox(frame_editar, values=categorias, state="readonly")
        combobox_categoria.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(frame_editar, text="Edad:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        combobox_edad = ttk.Combobox(frame_editar, values=edades, state="readonly")
        combobox_edad.grid(row=3, column=1, padx=5, pady=5)

        # Crear botones a la derecha de las listas desplegables
        boton_guardar = tk.Button(frame_editar, text="Guardar Cambios", command=lambda: guardar_cambios(), bg="lightgreen")
        boton_guardar.grid(row=0, column=2, padx=10, pady=5, sticky="w")

        boton_nuevo = tk.Button(frame_editar, text="Nuevo Participante", command=lambda: nuevo_participante(), bg="lightblue")
        boton_nuevo.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        boton_eliminar = tk.Button(frame_editar, text="Eliminar Participante", command=lambda: eliminar_participante(), bg="red")
        boton_eliminar.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        # Nuevo botón para ordenar alfabéticamente
        boton_ordenar = tk.Button(frame_editar, text="Orden Alfabético", command=lambda: ordenar_alfabeticamente(), bg="orange")
        boton_ordenar.grid(row=3, column=2, padx=10, pady=5, sticky="w")

        # Función para cargar datos del participante seleccionado
        def cargar_participante(event):
            item = tree.selection()
            if item:
                valores = tree.item(item, "values")
                entrada_nombre.delete(0, tk.END)
                entrada_nombre.insert(0, valores[0])
                combobox_sexo.set(valores[1])
                combobox_categoria.set(valores[2])
                combobox_edad.set(valores[3])

        # Vincular selección del Treeview con la carga de datos
        tree.bind("<<TreeviewSelect>>", cargar_participante)

        # Función para guardar cambios en el participante
        def guardar_cambios():
            item = tree.selection()
            if item:
                valores = (
                    entrada_nombre.get(),
                    combobox_sexo.get(),
                    combobox_categoria.get(),
                    combobox_edad.get(),
                )
                tree.item(item, values=valores)

                # Actualizar la lista de participantes
                index = tree.index(item)
                self.participantes[index] = {
                    "nombre": valores[0],
                    "sexo": valores[1],
                    "categoria": valores[2],
                    "edad": valores[3],
                }

                # Guardar cambios en el archivo JSON
                with open("participantes.json", "w") as file:
                    json.dump(self.participantes, file, indent=4)

                messagebox.showinfo("Éxito", "Cambios guardados correctamente.")

        # Función para agregar un nuevo participante
        def nuevo_participante():
            nuevo = {
                "nombre": entrada_nombre.get(),
                "sexo": combobox_sexo.get(),
                "categoria": combobox_categoria.get(),
                "edad": combobox_edad.get(),
            }
            if all(nuevo.values()):  # Verificar que todos los campos estén llenos
                self.participantes.append(nuevo)
                tree.insert("", tk.END, values=(nuevo["nombre"], nuevo["sexo"], nuevo["categoria"], nuevo["edad"]))

                # Guardar cambios en el archivo JSON
                with open("participantes.json", "w") as file:
                    json.dump(self.participantes, file, indent=4)

                messagebox.showinfo("Éxito", "Nuevo participante agregado.")
            else:
                messagebox.showerror("Error", "Por favor, complete todos los campos.")

        # Función para eliminar un participante seleccionado
        def eliminar_participante():
            item = tree.selection()
            if item:
                index = tree.index(item)
                tree.delete(item)
                del self.participantes[index]

                # Guardar cambios en el archivo JSON
                with open("participantes.json", "w") as file:
                    json.dump(self.participantes, file, indent=4)

                messagebox.showinfo("Éxito", "Participante eliminado.")
            else:
                messagebox.showerror("Error", "Por favor, seleccione un participante para eliminar.")

        # Función para ordenar participantes alfabéticamente
        def ordenar_alfabeticamente():
            self.participantes.sort(key=lambda p: p["nombre"])  # Ordenar por nombre
            tree.delete(*tree.get_children())  # Limpiar el Treeview

            # Volver a insertar los participantes ordenados
            for participante in self.participantes:
                tree.insert("", tk.END, values=(participante["nombre"], participante["sexo"], participante["categoria"], participante["edad"]))

            # Guardar cambios en el archivo JSON
            with open("participantes.json", "w") as file:
                json.dump(self.participantes, file, indent=4)

            messagebox.showinfo("Éxito", "Participantes ordenados alfabéticamente.")

    def generar_programa(self):
        # Obtener las partes agregadas al lienzo (pueden repetirse)
        partes_en_lienzo = [
            self.lienzo.itemcget(item, "text")
            for item in self.lienzo.find_withtag("parte")
        ]

        # Generar identificadores únicos para partes repetidas
        contador_partes = {}
        partes_unicas = []
        for parte in partes_en_lienzo:
            if parte not in contador_partes:
                contador_partes[parte] = 1
            else:
                contador_partes[parte] += 1
            parte_id = parte if contador_partes[parte] == 1 else f"{parte} ({contador_partes[parte]})"
            partes_unicas.append(parte_id)

        # Asignar participantes a todas las partes en el lienzo
        self.asignaciones = asignar_participantes(partes_unicas, self.participantes.copy())
        self.mostrar_asignaciones()

    def mostrar_asignaciones(self):
        self.lienzo.delete("all")  # Limpiar el lienzo
        self.botones_reemplazar = []  # Lista para rastrear los botones
        y = 20  # Posición inicial en el lienzo

        # Mostrar las asignaciones en el orden generado (incluyendo partes repetidas)
        for parte_id, asignado in self.asignaciones.items():
            if isinstance(asignado, dict):  # Si es una demostración con titular y acompañante
                # Mostrar el título de la parte
                self.lienzo.create_text(10, y, text=f"{parte_id}:", anchor="w", tags=("asignacion",))

                # Mostrar el titular en la misma fila, con más espacio a la izquierda
                self.lienzo.create_text(250, y, text=f"Titular: {asignado['titular']}", anchor="w", tags=("asignacion",))

                # Mostrar el acompañante en la fila siguiente, alineado con el título "Titular:"
                self.lienzo.create_text(250, y + 20, text=f"Acompañante: {asignado['acompanante']}", anchor="w", tags=("asignacion",))

                # Crear un botón "Reemplazar" para el titular
                boton_reemplazar = tk.Button(
                    self.lienzo,
                    text="Reemplazar Titular",
                    command=lambda p=parte_id: self.reemplazar_participante(p),
                    bg="pink",
                    height=1  # Reducir altura del botón
                )
                boton_id = self.lienzo.create_window(500, y, window=boton_reemplazar, anchor="w", tags=("boton_reemplazar",))
                self.botones_reemplazar.append((boton_id, y))  # Guardar la referencia del botón y su posición

                # Crear un botón "Reemplazar Acompañante" debajo del botón "Reemplazar Titular"
                boton_reemplazar_acompanante = tk.Button(
                    self.lienzo,
                    text="Reemplazar Acompañante",
                    command=lambda p=parte_id: self.reemplazar_acompanante(p),
                    bg="lightgreen",
                    height=1  # Reducir altura del botón
                )
                boton_acompanante_id = self.lienzo.create_window(500, y + 25, window=boton_reemplazar_acompanante, anchor="w", tags=("boton_reemplazar_acompanante",))
                self.botones_reemplazar.append((boton_acompanante_id, y + 25))  # Guardar la referencia del botón y su posición

                y += 60  # Espaciado entre asignaciones con acompañante
            else:
                # Mostrar el título de la parte y el asignado en la misma fila, con más espacio a la izquierda
                self.lienzo.create_text(10, y, text=f"{parte_id}:", anchor="w", tags=("asignacion",))
                self.lienzo.create_text(250, y, text=f"{asignado}", anchor="w", tags=("asignacion",))

                # Crear un botón "Reemplazar" normal con altura reducida
                boton_reemplazar = tk.Button(
                    self.lienzo,
                    text="Reemplazar",
                    command=lambda p=parte_id: self.reemplazar_participante(p),
                    bg="pink",
                    height=1  # Reducir altura del botón a la mitad
                )
                boton_id = self.lienzo.create_window(500, y, window=boton_reemplazar, anchor="w", tags=("boton_reemplazar",))
                self.botones_reemplazar.append((boton_id, y))  # Guardar la referencia del botón y su posición

                y += 30  # Espaciado entre asignaciones normales

        # Actualizar la región de desplazamiento del lienzo
        self.lienzo.configure(scrollregion=self.lienzo.bbox("all"))

        # Vincular el redimensionamiento del lienzo para ajustar los botones
        self.lienzo.bind("<Configure>", self.actualizar_botones)

    def actualizar_botones(self, event):
        # Recalcular la posición de los botones "Reemplazar" al redimensionar el lienzo
        ancho_lienzo = event.width
        for boton_id, y in self.botones_reemplazar:
            self.lienzo.coords(boton_id, ancho_lienzo - 100, y)  # Ajustar al extremo derecho

    def guardar_programa(self):
        with open("programa.json", "w") as file:
            json.dump(self.asignaciones, file, indent=4)
        messagebox.showinfo("Guardado", "El programa ha sido guardado exitosamente.")

    def reemplazar_participante(self, parte_seleccionada):
        posibles = [p for p in self.participantes if reglas_elegibilidad(parte_seleccionada, p)]
        if posibles:
            asignado = random.choice(posibles)
            if isinstance(self.asignaciones[parte_seleccionada], dict):  # Si es una asignación con titular y acompañante
                self.asignaciones[parte_seleccionada]['titular'] = asignado['nombre']
            else:  # Si es una asignación normal
                self.asignaciones[parte_seleccionada] = asignado['nombre']
            self.mostrar_asignaciones()
        else:
            messagebox.showerror("Error", "No hay opciones válidas para reemplazar")

    def reemplazar_acompanante(self, parte_seleccionada):
        asignacion = self.asignaciones.get(parte_seleccionada)
        if not isinstance(asignacion, dict) or "acompanante" not in asignacion:
            messagebox.showerror("Error", "La parte seleccionada no tiene un acompañante asignado.")
            return

        titular = asignacion['titular']

        # Cargar historial
        historial = cargar_historial()

        # Filtrar posibles acompañantes según las reglas relajadas
        posibles_acompanantes = [
            p for p in self.participantes
            if p["nombre"] != titular  # No puede ser el titular
            and p["nombre"] != asignacion.get("acompanante", "")  # No puede ser el acompañante actual
            and p["edad"] != "niño"  # Niños no pueden ser acompañantes
            and p["sexo"] == next((t["sexo"] for t in self.participantes if t["nombre"] == titular), None)  # Mismo sexo
        ]

        # Priorizar combinación de publicador fuerte con débil
        publicador_fuerte = next((p for p in self.participantes if p["nombre"] == titular and p["categoria"] == "Publicador Fuerte"), None)
        publicador_debil = next((p for p in self.participantes if p["nombre"] == titular and p["categoria"] == "Publicador Débil"), None)

        if publicador_fuerte:
            posibles_acompanantes = [
                p for p in posibles_acompanantes if p["categoria"] == "Publicador Débil"
            ] or posibles_acompanantes  # Si no hay débiles, usar todos los posibles
        elif publicador_debil:
            posibles_acompanantes = [
                p for p in posibles_acompanantes if p["categoria"] == "Publicador Fuerte"
            ] or posibles_acompanantes  # Si no hay fuertes, usar todos los posibles

        # Si todos tienen igual número de participaciones, elegir al azar
        if posibles_acompanantes:
            min_participaciones = min(historial.get(p["nombre"], 0) for p in posibles_acompanantes)
            menos_recientes = [
                p for p in posibles_acompanantes if historial.get(p["nombre"], 0) == min_participaciones
            ]
            nuevo_acompanante = random.choice(menos_recientes)  # Elegir al azar entre los menos recientes

            # Actualizar la asignación con el nuevo acompañante
            self.asignaciones[parte_seleccionada]['acompanante'] = nuevo_acompanante['nombre']

            # Refrescar la interfaz
            self.mostrar_asignaciones()
        else:
            messagebox.showerror("Error", "No hay opciones válidas para reemplazar al acompañante.")

    def ver_historial(self):
        """Abrir una ventana para mostrar el historial de los participantes."""
        ventana_historial = tk.Toplevel(self.root)
        ventana_historial.title("Historial de Participantes")
        ventana_historial.geometry("700x500")  # Tamaño de la ventana

        # Crear un marco para la lista del historial
        frame_historial = tk.Frame(ventana_historial)
        frame_historial.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear un Treeview para mostrar el historial
        columnas = ("nombre", "asignacion", "fecha")
        tree = ttk.Treeview(frame_historial, columns=columnas, show="headings")
        tree.pack(fill=tk.BOTH, expand=True)

        # Configurar encabezados
        for col in columnas:
            tree.heading(col, text=col.capitalize())

        # Cargar datos del historial desde el archivo JSON
        try:
            with open("historial.json", "r") as file:
                historial = json.load(file)
                for nombre, asignaciones in historial.items():
                    for asignacion in asignaciones:
                        tree.insert("", tk.END, values=(nombre, asignacion["asignacion"], asignacion["fecha"]))
        except FileNotFoundError:
            messagebox.showerror("Error", "El archivo historial.json no existe.")

def obtener_categorias():
    """Extraer categorías únicas del archivo participantes.json."""
    try:
        with open("participantes.json", "r") as file:
            participantes = json.load(file)
            categorias = {p["categoria"] for p in participantes}
            return sorted(categorias)  # Devolver categorías ordenadas
    except FileNotFoundError:
        return []

def obtener_opciones_campo(campo):
    """Extraer valores únicos de un campo específico del archivo participantes.json."""
    try:
        with open("participantes.json", "r") as file:
            participantes = json.load(file)
            opciones = {p[campo] for p in participantes if campo in p}
            return sorted(opciones)  # Devolver opciones ordenadas
    except FileNotFoundError:
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.mainloop()
{
  "python.terminal.shellIntegration.enabled": "true"
}