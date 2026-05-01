import customtkinter as ctk
import pyotp
import json
import os
import hashlib
from datetime import datetime

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ── Rutas ────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# cuentas_seguras.json lo escribe admin; apuntamos a admin/data/ desde cliente/
ADMIN_DATA_DIR = os.path.join(BASE_DIR, "..", "admin", "data")
DB_CONFIG  = os.path.join(ADMIN_DATA_DIR, "cuentas_seguras.json")

DB_AGENDAS = os.path.join(DATA_DIR, "agendas_usuarios.json")  # solo cliente escribe aquí
# ─────────────────────────────────────────────────────────────────────────────

class AppCliente(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Terminal de Acceso Seguro")
        self.geometry("550x650")
        self.db_agendas = self.cargar_agendas()
        self.mostrar_login()

    def cargar_config_seguridad(self):
        if os.path.exists(DB_CONFIG):
            try:
                with open(DB_CONFIG, "r") as f:
                    return json.load(f)
            except:
                return None
        return None

    def cargar_agendas(self):
        if os.path.exists(DB_AGENDAS):
            try:
                with open(DB_AGENDAS, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def guardar_agendas(self):
        with open(DB_AGENDAS, "w") as f:
            json.dump(self.db_agendas, f, indent=4)

    def mostrar_login(self):
        self.limpiar_interfaz()

        ctk.CTkLabel(self, text="SISTEMA DE ACCESO PRIVADO", font=("Helvetica", 22, "bold")).pack(pady=40)

        ctk.CTkLabel(self, text="Identificador de Usuario:", font=("bold", 12)).pack(pady=5)
        self.entry_user = ctk.CTkEntry(self, placeholder_text="Nombre de usuario", width=300)
        self.entry_user.pack(pady=10)

        ctk.CTkLabel(self, text="Código de Seguridad (TOTP):", font=("bold", 12)).pack(pady=5)
        self.entry_otp = ctk.CTkEntry(self, placeholder_text="000000", justify="center",
                                      font=("Arial", 24), width=300)
        self.entry_otp.pack(pady=10)

        ctk.CTkButton(self, text="VALIDAR IDENTIDAD", fg_color="#28a745",
                      height=45, command=self.validar).pack(pady=30)

        self.lbl_info = ctk.CTkLabel(self, text="", text_color="red")
        self.lbl_info.pack()

    def validar(self):
        data = self.cargar_config_seguridad()
        if not data:
            self.lbl_info.configure(text="Error: Sistema no configurado")
            return

        user_input = self.entry_user.get().strip().lower()
        otp_input  = self.entry_otp.get().strip()

        acceso_concedido = False

        if user_input in data["usuarios"]:
            u_cfg = data["usuarios"][user_input]
            algos = {"sha1": hashlib.sha1, "sha256": hashlib.sha256, "sha512": hashlib.sha512}
            totp  = pyotp.totp.TOTP(
                u_cfg["secret"],
                interval=u_cfg["interval"],
                digits=u_cfg["digits"],
                digest=algos.get(u_cfg.get("algo", "sha1"))
            )
            if totp.verify(otp_input, valid_window=u_cfg.get("window", 0)):
                acceso_concedido = True

        if acceso_concedido:
            print(f"[LOG {datetime.now()}] Acceso exitoso para: {user_input}")
            self.mostrar_menu_post_login(user_input)
        else:
            print(f"[LOG {datetime.now()}] Intento fallido para: {user_input}")
            self.lbl_info.configure(text="Credenciales inválidas")
            self.entry_otp.delete(0, "end")

    def mostrar_menu_post_login(self, usuario):
        self.limpiar_interfaz()
        ctk.CTkLabel(self, text=f"BIENVENIDO, {usuario.upper()}",
                     font=("bold", 18), text_color="#2ecc71").pack(pady=30)

        frame_btns = ctk.CTkFrame(self)
        frame_btns.pack(pady=20, padx=40, fill="both")

        ctk.CTkButton(frame_btns, text="📂 CONSULTAR MI AGENDA", height=60,
                      command=lambda: self.mostrar_agenda(usuario)).pack(pady=15, padx=20, fill="x")
        ctk.CTkButton(frame_btns, text="➕ AÑADIR NUEVO DATO", height=60, fg_color="#3498db",
                      command=lambda: self.ventana_añadir_datos(usuario)).pack(pady=15, padx=20, fill="x")

        ctk.CTkButton(self, text="Cerrar Sesión", fg_color="gray",
                      command=self.mostrar_login).pack(pady=40)

    def mostrar_agenda(self, usuario):
        self.limpiar_interfaz()
        ctk.CTkLabel(self, text=f"REGISTROS DE {usuario.upper()}", font=("bold", 16)).pack(pady=20)

        scroll = ctk.CTkScrollableFrame(self, width=450, height=350)
        scroll.pack(pady=10)

        datos = self.db_agendas.get(usuario.lower(), [])
        if not datos:
            ctk.CTkLabel(scroll, text="No hay datos registrados.").pack(pady=20)

        for t, d in datos:
            f = ctk.CTkFrame(scroll)
            f.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(f, text=t, font=("bold", 12), text_color="#3498db").pack(side="left", padx=10)
            ctk.CTkLabel(f, text=d).pack(side="right", padx=10)

        ctk.CTkButton(self, text="Volver al Menú",
                      command=lambda: self.mostrar_menu_post_login(usuario)).pack(pady=20)

    def ventana_añadir_datos(self, usuario):
        self.limpiar_interfaz()
        ctk.CTkLabel(self, text="NUEVO REGISTRO EN AGENDA", font=("bold", 16)).pack(pady=20)

        e_titulo = ctk.CTkEntry(self, placeholder_text="Concepto (ej: Clave Caja)", width=300)
        e_titulo.pack(pady=10)
        e_valor  = ctk.CTkEntry(self, placeholder_text="Valor (ej: 4432)", width=300)
        e_valor.pack(pady=10)

        def guardar():
            t, v = e_titulo.get(), e_valor.get()
            if t and v:
                u_key = usuario.lower()
                if u_key not in self.db_agendas:
                    self.db_agendas[u_key] = []
                self.db_agendas[u_key].append([t, v])
                self.guardar_agendas()
                self.mostrar_menu_post_login(usuario)

        ctk.CTkButton(self, text="GUARDAR", fg_color="#28a745", command=guardar).pack(pady=20)
        ctk.CTkButton(self, text="CANCELAR", fg_color="gray",
                      command=lambda: self.mostrar_menu_post_login(usuario)).pack()

    def limpiar_interfaz(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    AppCliente().mainloop()
