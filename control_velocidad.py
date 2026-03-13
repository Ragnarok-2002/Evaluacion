import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import json
import os

# ─────────────────────────────────────────────
# INTENTAMOS importar fpdf2 para generar PDFs
# Si no está instalado, lo indicamos al usuario
# ─────────────────────────────────────────────
try:
    from fpdf import FPDF
    PDF_DISPONIBLE = True
except ImportError:
    PDF_DISPONIBLE = False

# ─────────────────────────────────────────────
# USUARIOS DEL SISTEMA (login)
# En un sistema real esto estaría en una base de datos
# Aquí usamos un diccionario simple: {usuario: contraseña}
# ─────────────────────────────────────────────
USUARIOS = {
    "admin": "sena123",
    "transito1": "bogota2026",
    "transito2": "velocidad1"
}

# ─────────────────────────────────────────────
# LISTA DE MULTAS REGISTRADAS EN ESTA SESIÓN
# Cada multa es un diccionario con los datos del registro
# ─────────────────────────────────────────────
multas_registradas = []


# ══════════════════════════════════════════════
# FUNCIÓN: evaluar_velocidad
# Recibe la velocidad ingresada y retorna:
# estado, tipo de infracción, valor de multa
# y si se retira el permiso de conducción
# ══════════════════════════════════════════════
def evaluar_velocidad(velocidad):
    if velocidad <= 100:
        # Velocidad dentro del límite permitido
        return "Permitido", "Sin infracción", 0, False

    elif velocidad <= 110:
        # Infracción leve: entre 101 y 110 km/h
        return "Infracción", "Leve", 1_100_000, False

    elif velocidad <= 120:
        # Infracción grave: entre 111 y 120 km/h
        return "Infracción", "Grave", 2_215_000, False

    else:
        # Infracción muy grave: más de 120 km/h
        # Además se retira el permiso de conducción por 1 mes
        return "Infracción", "Muy Grave", 10_000_000, True


# ══════════════════════════════════════════════
# FUNCIÓN: registrar_multa
# Guarda el resultado de una evaluación en la
# lista de multas_registradas para luego
# poder exportarlas al PDF
# ══════════════════════════════════════════════
def registrar_multa(placa, velocidad, estado, tipo, valor, retiro_permiso):
    multa = {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "placa": placa.upper(),
        "velocidad": velocidad,
        "estado": estado,
        "tipo_infraccion": tipo,
        "valor_multa": valor,
        "retiro_permiso": retiro_permiso
    }
    multas_registradas.append(multa)


# ══════════════════════════════════════════════
# FUNCIÓN: generar_pdf
# Toma todas las multas registradas en la sesión
# y genera un archivo PDF con el reporte
# ══════════════════════════════════════════════
# Ahora recibe el nombre del usuario que generó el reporte
def generar_pdf(usuario):
    if not PDF_DISPONIBLE:
        messagebox.showerror("Error", "Instala fpdf2 con: pip install fpdf2")
        return

    if not multas_registradas:
        messagebox.showwarning("Sin datos", "No hay multas registradas aún.")
        return

    # Creamos el documento PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Título del reporte
    pdf.cell(0, 10, "REPORTE DE INFRACCIONES - TRÁNSITO BOGOTÁ D.C.", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="C")
    # Muestra el nombre del operador que generó el reporte
    pdf.cell(0, 8, f"Operador: {usuario}", ln=True, align="C")
    pdf.ln(5)

    # Encabezados de la tabla
    pdf.set_font("Arial", "B", 10)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(30, 8, "Fecha", border=1, fill=True)
    pdf.cell(20, 8, "Placa", border=1, fill=True)
    pdf.cell(25, 8, "Velocidad", border=1, fill=True)
    pdf.cell(25, 8, "Estado", border=1, fill=True)
    pdf.cell(30, 8, "Tipo", border=1, fill=True)
    pdf.cell(30, 8, "Valor Multa", border=1, fill=True)
    pdf.cell(30, 8, "Retiro Permiso", border=1, ln=True, fill=True)

    # Filas con los datos de cada multa
    pdf.set_font("Arial", "", 9)
    for m in multas_registradas:
        pdf.cell(30, 8, m["fecha"][:10], border=1)
        pdf.cell(20, 8, m["placa"], border=1)
        pdf.cell(25, 8, f'{m["velocidad"]} km/h', border=1)
        pdf.cell(25, 8, m["estado"], border=1)
        pdf.cell(30, 8, m["tipo_infraccion"], border=1)
        pdf.cell(30, 8, f'${m["valor_multa"]:,}', border=1)
        pdf.cell(30, 8, "SÍ - 1 mes" if m["retiro_permiso"] else "No", border=1, ln=True)

    # Guardamos el PDF en el escritorio o carpeta actual
    nombre_archivo = f"reporte_infracciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(nombre_archivo)
    messagebox.showinfo("PDF Generado", f"Reporte guardado como:\n{nombre_archivo}")


# ══════════════════════════════════════════════
# CLASE: VentanaLogin
# Es la primera pantalla que ve el usuario
# Valida usuario y contraseña antes de entrar
# ══════════════════════════════════════════════
class VentanaLogin:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Control de Velocidad - Login")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # Construimos la interfaz del login
        self.construir_interfaz()

    def construir_interfaz(self):
        # Marco principal con padding
        marco = tk.Frame(self.root, padx=40, pady=30)
        marco.pack(expand=True)

        # Título
        tk.Label(marco, text="CONTROL DE VELOCIDAD", font=("Arial", 14, "bold")).pack(pady=(0, 5))
        tk.Label(marco, text="Tránsito Bogotá D.C.", font=("Arial", 10)).pack(pady=(0, 20))

        # Campo usuario
        tk.Label(marco, text="Usuario:", font=("Arial", 10)).pack(anchor="w")
        self.entry_usuario = tk.Entry(marco, width=30, font=("Arial", 10))
        self.entry_usuario.pack(pady=(0, 10))

        # Campo contraseña (muestra asteriscos)
        tk.Label(marco, text="Contraseña:", font=("Arial", 10)).pack(anchor="w")
        self.entry_password = tk.Entry(marco, width=30, show="*", font=("Arial", 10))
        self.entry_password.pack(pady=(0, 20))

        # Botón ingresar
        tk.Button(marco, text="Ingresar", width=20, font=("Arial", 10),
                  command=self.verificar_login).pack()

        # Permitir login con la tecla Enter
        self.root.bind("<Return>", lambda e: self.verificar_login())

    # ─────────────────────────────────────────
    # Verifica si el usuario y contraseña
    # existen en el diccionario USUARIOS
    # ─────────────────────────────────────────
    def verificar_login(self):
        usuario = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        if usuario in USUARIOS and USUARIOS[usuario] == password:
            # Login correcto: cerramos esta ventana y abrimos el sistema principal
            self.root.destroy()
            root_principal = tk.Tk()
            VentanaPrincipal(root_principal, usuario)
            root_principal.mainloop()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")


# ══════════════════════════════════════════════
# CLASE: VentanaPrincipal
# Es la pantalla principal del sistema después
# de iniciar sesión correctamente
# ══════════════════════════════════════════════
class VentanaPrincipal:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.root.title(f"Control de Velocidad - Usuario: {usuario}")
        self.root.geometry("650x550")

        self.construir_interfaz()

    def construir_interfaz(self):
        # ── Encabezado ──
        tk.Label(self.root, text="SISTEMA DE CONTROL DE VELOCIDAD VEHICULAR",
                 font=("Arial", 13, "bold")).pack(pady=10)
        tk.Label(self.root, text=f"Operador: {self.usuario}",
                 font=("Arial", 9)).pack()

        # ── Marco de entrada de datos ──
        marco_entrada = tk.LabelFrame(self.root, text="Registro de Vehículo", padx=15, pady=10)
        marco_entrada.pack(padx=20, pady=10, fill="x")

        # Campo placa
        tk.Label(marco_entrada, text="Placa del vehículo:", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
        self.entry_placa = tk.Entry(marco_entrada, width=15, font=("Arial", 10))
        self.entry_placa.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Campo velocidad
        tk.Label(marco_entrada, text="Velocidad detectada (km/h):", font=("Arial", 10)).grid(row=1, column=0, sticky="w")
        self.entry_velocidad = tk.Entry(marco_entrada, width=15, font=("Arial", 10))
        self.entry_velocidad.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Botón evaluar
        tk.Button(marco_entrada, text="Evaluar Velocidad", font=("Arial", 10),
                  command=self.evaluar).grid(row=2, column=0, columnspan=2, pady=10)

        # ── Marco de resultado ──
        marco_resultado = tk.LabelFrame(self.root, text="Resultado", padx=15, pady=10)
        marco_resultado.pack(padx=20, pady=5, fill="x")

        self.label_estado = tk.Label(marco_resultado, text="Estado: -", font=("Arial", 10))
        self.label_estado.pack(anchor="w")
        self.label_tipo = tk.Label(marco_resultado, text="Tipo de infracción: -", font=("Arial", 10))
        self.label_tipo.pack(anchor="w")
        self.label_multa = tk.Label(marco_resultado, text="Valor multa: -", font=("Arial", 10))
        self.label_multa.pack(anchor="w")
        self.label_permiso = tk.Label(marco_resultado, text="", font=("Arial", 10, "bold"), fg="red")
        self.label_permiso.pack(anchor="w")

        # ── Historial de registros en esta sesión ──
        marco_historial = tk.LabelFrame(self.root, text="Historial de esta sesión", padx=10, pady=5)
        marco_historial.pack(padx=20, pady=5, fill="both", expand=True)

        # Tabla con columnas
        columnas = ("Placa", "Velocidad", "Tipo", "Valor Multa", "Retiro Permiso")
        self.tabla = ttk.Treeview(marco_historial, columns=columnas, show="headings", height=6)
        for col in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=110)
        self.tabla.pack(fill="both", expand=True)

        # ── Botones inferiores ──
        marco_botones = tk.Frame(self.root)
        marco_botones.pack(pady=10)

# Pasamos el usuario actual a la función para que quede registrado en el PDF
        tk.Button(marco_botones, text="Generar PDF", font=("Arial", 10),
          command=lambda: generar_pdf(self.usuario)).pack(side="left", padx=10)
        tk.Button(marco_botones, text="Limpiar campos", font=("Arial", 10),
                  command=self.limpiar_campos).pack(side="left", padx=10)
        tk.Button(marco_botones, text="Cerrar sesión", font=("Arial", 10),
                  command=self.cerrar_sesion).pack(side="left", padx=10)

    # ─────────────────────────────────────────
    # Toma los datos del formulario, evalúa
    # la velocidad y muestra el resultado
    # ─────────────────────────────────────────
    def evaluar(self):
        placa = self.entry_placa.get().strip()
        velocidad_texto = self.entry_velocidad.get().strip()

        # Validamos que los campos no estén vacíos
        if not placa or not velocidad_texto:
            messagebox.showwarning("Campos vacíos", "Por favor ingresa la placa y la velocidad.")
            return

        # Validamos que la velocidad sea un número
        try:
            velocidad = float(velocidad_texto)
        except ValueError:
            messagebox.showerror("Error", "La velocidad debe ser un número.")
            return

        # Evaluamos la velocidad con la lógica del sistema
        estado, tipo, valor, retiro = evaluar_velocidad(velocidad)

        # Mostramos el resultado en pantalla
        self.label_estado.config(text=f"Estado: {estado}")
        self.label_tipo.config(text=f"Tipo de infracción: {tipo}")
        self.label_multa.config(text=f"Valor multa: ${valor:,} COP")

        if retiro:
            self.label_permiso.config(text="⚠ PERMISO DE CONDUCCIÓN RETIRADO POR 1 MES")
        else:
            self.label_permiso.config(text="")

        # Guardamos el registro en la lista de multas
        registrar_multa(placa, velocidad, estado, tipo, valor, retiro)

        # Agregamos la fila al historial visible
        self.tabla.insert("", "end", values=(
            placa.upper(),
            f"{velocidad} km/h",
            tipo,
            f"${valor:,}",
            "SÍ - 1 mes" if retiro else "No"
        ))

    # ─────────────────────────────────────────
    # Limpia los campos de entrada y el resultado
    # ─────────────────────────────────────────
    def limpiar_campos(self):
        self.entry_placa.delete(0, tk.END)
        self.entry_velocidad.delete(0, tk.END)
        self.label_estado.config(text="Estado: -")
        self.label_tipo.config(text="Tipo de infracción: -")
        self.label_multa.config(text="Valor multa: -")
        self.label_permiso.config(text="")

    # ─────────────────────────────────────────
    # Cierra la sesión actual y vuelve al login
    # ─────────────────────────────────────────
    def cerrar_sesion(self):
        self.root.destroy()
        root_login = tk.Tk()
        VentanaLogin(root_login)
        root_login.mainloop()


# ══════════════════════════════════════════════
# PUNTO DE ENTRADA DEL PROGRAMA
# Aquí arranca todo cuando ejecutas el archivo
# ══════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    VentanaLogin(root)
    root.mainloop()