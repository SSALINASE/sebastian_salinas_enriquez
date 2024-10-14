import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import datetime

def ConectarBaseDatos():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="", 
            database="gestionenvios"
        )
        return conexion
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Comprueba las credenciales de la base de datos: {err}")
        return None

def AgregarEnvio():
    NumeroSeguimiento = entry_NumeroSeguimiento.get()
    origen = entry_origen.get()
    destino = entry_destino.get()
    fecha_entrega = entry_fecha_entrega.get()
    estado = "En tránsito"

    if not NumeroSeguimiento or not origen or not destino or not fecha_entrega:
        messagebox.showwarning("Advertencia", "Todos los campos son necesarios.")
        return

    try:
        fecha_entrega_datetime = datetime.strptime(fecha_entrega, '%d/%m/%Y').date()
    except ValueError:
        messagebox.showwarning("Advertencia", "Fecha de entrega debe estar en formato DD/MM/YYYY.")
        return

    conexion = ConectarBaseDatos()
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "INSERT INTO Envios (NumeroSeguimiento, Origen, Destino, FechaEntregaPrevista, Estado) "
                "VALUES (%s, %s, %s, %s, %s)",
                (NumeroSeguimiento, origen, destino, fecha_entrega_datetime, estado)
            )
            conexion.commit()
            messagebox.showinfo("Éxito", "Envío agregado exitosamente.")
            MostrarEnvios()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al agregar envío: {err}")
        finally:
            cursor.close()
            conexion.close()

def MostrarEnvios():
    conexion = ConectarBaseDatos()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM Envios")
        filas = cursor.fetchall()
        tabla_envios.delete(*tabla_envios.get_children())
        for index, fila in enumerate(filas):
            fecha_entrega = fila[4].strftime('%d/%m/%Y') if fila[4] else ''
            fila_mostrada = (fila[0], fila[1], fila[2], fila[3], fecha_entrega, fila[5])
            if index % 2 == 0:
                tabla_envios.insert("", "end", values=fila_mostrada, tags=('evenrow',))
            else:
                tabla_envios.insert("", "end", values=fila_mostrada, tags=('oddrow',))
        cursor.close()
        conexion.close()

def ActualizarEnvio():
    selected_item = tabla_envios.selection()
    if not selected_item:
        messagebox.showwarning("Advertencia", "Selecciona un envío para actualizar.")
        return

    envio_id = tabla_envios.item(selected_item)["values"][0]
    NuevoEstado = entry_estado.get()

    if not NuevoEstado:
        messagebox.showwarning("Advertencia", "El campo de estado no puede estar vacío.")
        return

    conexion = ConectarBaseDatos()
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute(
                "UPDATE Envios SET Estado = %s WHERE ID = %s",
                (NuevoEstado, envio_id)
            )
            conexion.commit()
            messagebox.showinfo("Éxito", "Estado del envío actualizado.")
            MostrarEnvios()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Error al actualizar el envío: {err}")
        finally:
            cursor.close()
            conexion.close()

root = tk.Tk()
root.title("Gestión de Envíos")
root.geometry("900x600")

style = ttk.Style()
style.configure('TButton', font=('Helvetica', 10), padding=5)
style.configure('TEntry', font=('Helvetica', 10), padding=5)
style.configure('Treeview', font=('Helvetica', 10), padding=5)
style.configure('Treeview.Heading', font=('Helvetica', 10, 'bold'))

frame_campos = ttk.Frame(root, padding=(10, 10))
frame_campos.pack(anchor='w', pady=10)

tk.Label(frame_campos, text="Número de Seguimiento").grid(row=0, column=0, padx=5, pady=5, sticky='w')
entry_NumeroSeguimiento = ttk.Entry(frame_campos)
entry_NumeroSeguimiento.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_campos, text="Origen").grid(row=1, column=0, padx=5, pady=5, sticky='w')
entry_origen = ttk.Entry(frame_campos)
entry_origen.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_campos, text="Destino").grid(row=2, column=0, padx=5, pady=5, sticky='w')
entry_destino = ttk.Entry(frame_campos)
entry_destino.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_campos, text="Fecha de Entrega (DD/MM/YYYY)").grid(row=3, column=0, padx=5, pady=5, sticky='w')
entry_fecha_entrega = ttk.Entry(frame_campos)
entry_fecha_entrega.grid(row=3, column=1, padx=5, pady=5)

tk.Label(frame_campos, text="Estado").grid(row=4, column=0, padx=5, pady=5, sticky='w')
entry_estado = ttk.Entry(frame_campos)
entry_estado.grid(row=4, column=1, padx=5, pady=5)

frame_botones = ttk.Frame(root)
frame_botones.pack(pady=10)

btn_agregar = ttk.Button(frame_botones, text="Agregar Envío", command=AgregarEnvio)
btn_agregar.grid(row=0, column=0, padx=5)

btn_actualizar = ttk.Button(frame_botones, text="Actualizar Estado", command=ActualizarEnvio)
btn_actualizar.grid(row=0, column=1, padx=5)

frame_tabla = ttk.Frame(root)
frame_tabla.pack(pady=10)

tabla_envios = ttk.Treeview(frame_tabla, columns=("ID", "NumeroSeguimiento", "Origen", "Destino", "FechaEntregaPrevista", "Estado"), show="headings")
tabla_envios.heading("ID", text="ID")
tabla_envios.heading("NumeroSeguimiento", text="Número de Seguimiento")
tabla_envios.heading("Origen", text="Origen")
tabla_envios.heading("Destino", text="Destino")
tabla_envios.heading("FechaEntregaPrevista", text="Fecha de Entrega Prevista")
tabla_envios.heading("Estado", text="Estado")

tabla_envios.column("ID", width=50, anchor='center')
tabla_envios.column("NumeroSeguimiento", width=150)
tabla_envios.column("Origen", width=100)
tabla_envios.column("Destino", width=100)
tabla_envios.column("FechaEntregaPrevista", width=120)
tabla_envios.column("Estado", width=100)

tabla_envios.tag_configure('oddrow', background='white')
tabla_envios.tag_configure('evenrow', background='lightblue')

tabla_envios.pack()
MostrarEnvios()
root.mainloop()
