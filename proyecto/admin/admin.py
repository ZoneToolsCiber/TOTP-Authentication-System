import customtkinter as ctk
import pyotp
import qrcode
import json
import os
from PIL import Image

ctk.set_appearance_mode("dark")

# ── Rutas ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_FILE  = os.path.join(DATA_DIR, "cuentas_seguras.json")   # solo admin escribe aquí
QR_DIR   = DATA_DIR                                          # QR guardados en admin/data/
# ─────────────────────────────────────────────────────────────────────────────

class AdminPanel(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("ADMIN: Configuración Total TOTP")
        self.geometry("650x900")
        self.imagen_qr_actual = None
        self.cuentas = self.cargar_datos()

        if "admin_master" not in self.cuentas:
            self.crear_token_maestro()
        else:
            self.mostrar_menu_principal()

    def cargar_datos(self):
        default = {"usuarios": {}}
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r") as f:
                    return json.load(f)
            except:
                return default
        return default

    def guardar_datos(self):
        with open(DB_FILE, "w") as f:
            json.dump(self.cuentas, f, indent=4)

    def crear_token_maestro(self):
        self.limpiar()
        ctk.CTkLabel(self, text="🛡️ CONFIGURACIÓN TOKEN MAESTRO", font=("bold", 20), text_color="orange").pack(pady=20)
        secret = pyotp.random_base32()
        self.cuentas["admin_master"] = {"secret": secret, "interval": 30, "digits": 6, "algo": "sha1"}
        self.guardar_datos()
        uri = pyotp.totp.TOTP(secret).provisioning_uri(name="ADMIN", issuer_name="MasterKey")
        qr_path = os.path.join(QR_DIR, "admin_master.png")
        qrcode.make(uri).save(qr_path)
        pil_img = Image.open(qr_path)
        self.imagen_qr_actual = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(250, 250))
        ctk.CTkLabel(self, image=self.imagen_qr_actual, text="").pack(pady=10)
        ctk.CTkButton(self, text="TOKEN ESCANEADO", command=self.mostrar_menu_principal).pack(pady=20)

    def mostrar_menu_principal(self):
        self.limpiar()
        ctk.CTkLabel(self, text="GESTOR DE IDENTIDADES SEGURAS", font=("Helvetica", 22, "bold")).pack(pady=20)
        ctk.CTkButton(self, text="+ REGISTRO AVANZADO DE USUARIO", fg_color="#1f538d", height=40,
                      command=self.ventana_registro_avanzado).pack(pady=20)
        self.scroll = ctk.CTkScrollableFrame(self, height=500)
        self.scroll.pack(fill="both", padx=20, pady=10)
        self.actualizar_lista()

    def ventana_registro_avanzado(self):
        v = ctk.CTkToplevel(self)
        v.title("Parámetros del Protocolo")
        v.geometry("450x650")
        v.attributes("-topmost", True)

        ctk.CTkLabel(v, text="Identificadores", font=("bold", 14)).pack(pady=10)
        e_name = ctk.CTkEntry(v, placeholder_text="Nombre/Email (Label)", width=300)
        e_name.pack(pady=5)
        e_issuer = ctk.CTkEntry(v, placeholder_text="Emisor (App Name)", width=300)
        e_issuer.insert(0, "CiberApp_Pro")
        e_issuer.pack(pady=5)

        ctk.CTkLabel(v, text="Configuración Técnica", font=("bold", 14)).pack(pady=10)

        ctk.CTkLabel(v, text="Algoritmo (Digest):").pack()
        s_algo = ctk.CTkSegmentedButton(v, values=["sha1", "sha256", "sha512"])
        s_algo.set("sha1")
        s_algo.pack(pady=5)

        ctk.CTkLabel(v, text="Intervalo (Period):").pack()
        s_time = ctk.CTkSegmentedButton(v, values=["15", "30", "60", "90"])
        s_time.set("30")
        s_time.pack(pady=5)

        ctk.CTkLabel(v, text="Longitud (Digits):").pack()
        s_digits = ctk.CTkSegmentedButton(v, values=["6", "8"])
        s_digits.set("6")
        s_digits.pack(pady=5)

        ctk.CTkLabel(v, text="Ventana de Validación (Tolerancia):").pack()
        s_win = ctk.CTkSegmentedButton(v, values=["0", "1", "2"])
        s_win.set("1")
        s_win.pack(pady=5)

        def guardar():
            nombre = e_name.get()
            if not nombre:
                return
            self.cuentas["usuarios"][nombre] = {
                "secret":   pyotp.random_base32(),
                "interval": int(s_time.get()),
                "digits":   int(s_digits.get()),
                "algo":     s_algo.get(),
                "window":   int(s_win.get()),
                "issuer":   e_issuer.get()
            }
            self.guardar_datos()
            v.destroy()
            self.actualizar_lista()

        ctk.CTkButton(v, text="GENERAR USUARIO", fg_color="#28a745", command=guardar).pack(pady=20)

    def actualizar_lista(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        for u in self.cuentas["usuarios"]:
            f = ctk.CTkFrame(self.scroll)
            f.pack(fill="x", pady=2)
            ctk.CTkLabel(f, text=f"👤 {u}").pack(side="left", padx=10)
            ctk.CTkButton(f, text="AUDITAR Y VER QR", width=140,
                          command=lambda x=u: self.verificar_maestro(x)).pack(side="right", padx=5)

    def verificar_maestro(self, usuario):
        token = ctk.CTkInputDialog(text=f"TOKEN MAESTRO para auditar a {usuario}:", title="Seguridad").get_input()
        if token:
            admin_s = self.cuentas["admin_master"]["secret"]
            if pyotp.totp.TOTP(admin_s).verify(token.strip()):
                self.mostrar_detalles_finales(usuario)

    def mostrar_detalles_finales(self, usuario):
        self.limpiar()
        u = self.cuentas["usuarios"][usuario]

        ctk.CTkLabel(self, text=f"FICHA TÉCNICA DE SEGURIDAD: {usuario.upper()}",
                     font=("bold", 18), text_color="#4CAF50").pack(pady=15)

        detalles_frame = ctk.CTkFrame(self)
        detalles_frame.pack(pady=10, padx=30, fill="x")

        config_info = [
            ("👤 Label/Name:",  usuario),
            ("🏢 Emisor:",      u["issuer"]),
            ("🔑 Clave Secreta:", u["secret"]),
            ("⏱️ Intervalo:",   f"{u['interval']}s"),
            ("🔢 Longitud:",    f"{u['digits']} dígitos"),
            ("🧬 Algoritmo:",   u["algo"].upper()),
            ("🎯 Ventana Val.:", f"±{u['window']} intervalo(s)")
        ]

        for i, val in config_info:
            row = ctk.CTkFrame(detalles_frame, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(row, text=i, font=("bold", 12)).pack(side="left")
            ctk.CTkLabel(row, text=val, font=("Consolas", 11), text_color="#3498db").pack(side="right")

        import hashlib
        digest_mod = (hashlib.sha1 if u["algo"] == "sha1"
                      else hashlib.sha256 if u["algo"] == "sha256"
                      else hashlib.sha512)

        uri = pyotp.totp.TOTP(
            u["secret"], interval=u["interval"], digits=u["digits"], digest=digest_mod
        ).provisioning_uri(name=usuario, issuer_name=u["issuer"])

        qr_path = os.path.join(QR_DIR, f"qr_{usuario}.png")
        qrcode.make(uri).save(qr_path)
        pil_img = Image.open(qr_path)
        self.imagen_qr_actual = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(250, 250))

        ctk.CTkLabel(self, image=self.imagen_qr_actual, text="").pack(pady=10)
        ctk.CTkButton(self, text="CERRAR", command=self.mostrar_menu_principal).pack(pady=10)

    def limpiar(self):
        for w in self.winfo_children():
            w.destroy()

if __name__ == "__main__":
    AdminPanel().mainloop()
