<div align="center">

# 🔐 TOTP Authentication System
### Implementación del Protocolo RFC 6238

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![RFC 6238](https://img.shields.io/badge/RFC-6238-orange?style=for-the-badge&logo=ietf&logoColor=white)](https://datatracker.ietf.org/doc/html/rfc6238)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Académico-blue?style=for-the-badge)]()

<br/>

> **Proyecto desarrollado como parte del Máster en Ciberseguridad**  
> Implementación práctica de autenticación de dos factores (2FA) mediante el estándar TOTP

<br/>

---

</div>

## 👨‍🎓 Sobre este repositorio

Soy estudiante del **Máster en Ciberseguridad** y este repositorio recoge uno de los proyectos prácticos realizados durante el programa: la implementación completa del protocolo **TOTP (Time-based One-Time Password)** definido en el estándar [RFC 6238](https://datatracker.ietf.org/doc/html/rfc6238).

Lo publico de forma abierta con una intención clara: **ayudar a otras personas que están exactamente en el mismo punto en el que yo estuve**, dando sus primeros pasos en ciberseguridad y queriendo entender cómo funciona por dentro la autenticación de dos factores que usamos a diario. La teoría está muy bien, pero ver el código funcionando marca la diferencia.

Si estás estudiando ciberseguridad, preparando una certificación, o simplemente tienes curiosidad por entender qué ocurre cuando Google Authenticator genera ese código de 6 dígitos que cambia cada 30 segundos — este proyecto es para ti.

> 💬 *"No publico esto porque sea perfecto. Lo publico porque ojalá yo hubiera encontrado algo así cuando empecé."*

<br/>

---

## 📋 Tabla de Contenidos

- [¿Qué es TOTP?](#-qué-es-totp)
- [Arquitectura del sistema](#-arquitectura-del-sistema)
- [Características implementadas](#-características-implementadas)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación y uso](#-instalación-y-uso)
- [Flujo de ejecución](#-flujo-de-ejecución)
- [Parámetros técnicos](#-parámetros-técnicos-rfc-6238)
- [Seguridad y decisiones de diseño](#-seguridad-y-decisiones-de-diseño)
- [Posibles mejoras](#-posibles-mejoras)
- [Recursos para aprender](#-recursos-para-aprender)

<br/>

---

## 🔍 ¿Qué es TOTP?

**TOTP** (*Time-based One-Time Password*) es el algoritmo que hay detrás de aplicaciones como Google Authenticator, Authy o Microsoft Authenticator. Genera códigos numéricos de corta duración (normalmente 6 dígitos cada 30 segundos) que sólo son válidos en ese instante de tiempo.

La clave del protocolo es elegante en su simplicidad:

```
TOTP(K, T) = HOTP(K, T)   donde   T = floor(tiempo_unix / intervalo)
```

Tanto el servidor como el cliente generan **el mismo código de forma independiente**, sin necesidad de comunicarse entre sí, porque ambos comparten el mismo secreto y conocen la hora actual. Si los códigos coinciden, la identidad queda verificada.

```
┌─────────────────────┐         ┌─────────────────────┐
│   Google Auth App   │         │      Servidor        │
│                     │         │                      │
│  Secreto + Tiempo   │──────▶  │  Secreto + Tiempo    │
│         │           │  mismo  │         │            │
│         ▼           │  código │         ▼            │
│    HMAC-SHA1(...)   │◀═══════▶│    HMAC-SHA1(...)    │
│         │           │         │         │            │
│    Código: 483291   │         │    Código: 483291 ✓  │
└─────────────────────┘         └─────────────────────┘
```

El estándar completo está definido en el **[RFC 6238 — IETF](https://datatracker.ietf.org/doc/html/rfc6238)**.

<br/>

---

## 🏛️ Arquitectura del sistema

El proyecto está compuesto por **dos aplicaciones independientes** con responsabilidades bien diferenciadas:

```
┌─────────────────────────────────────────────────────────┐
│                    ECOSISTEMA TOTP                       │
│                                                         │
│   ┌───────────────────┐     ┌───────────────────────┐   │
│   │    admin.py       │     │     cliente.py        │   │
│   │                   │     │                       │   │
│   │  Panel de Admin   │     │  Terminal de Acceso   │   │
│   │  con Token Maestro│     │  Validación Ciega     │   │
│   │                   │     │                       │   │
│   │  - Registra users │     │  - Login con TOTP     │   │
│   │  - Genera QR      │     │  - Agenda privada     │   │
│   │  - Audita cuentas │     │  - Sesión segura      │   │
│   └────────┬──────────┘     └───────────┬───────────┘   │
│            │                            │               │
│            ▼                            ▼               │
│   ┌─────────────────┐       ┌─────────────────────┐     │
│   │cuentas_seguras  │       │  agendas_usuarios   │     │
│   │    .json        │       │       .json         │     │
│   │ (configuración  │       │  (datos privados    │     │
│   │  criptográfica) │       │   del usuario)      │     │
│   └─────────────────┘       └─────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

<br/>

---

## ✅ Características implementadas

### `admin.py` — Panel de Administración
- 🛡️ **Token Maestro propio** — el administrador tiene su propio TOTP para proteger las auditorías
- 👤 **Registro avanzado de usuarios** — con parámetros TOTP completamente configurables
- 📱 **Generación de QR** — compatible con Google Authenticator
- 🔍 **Auditoría protegida** — ver la ficha técnica de cualquier usuario requiere el token maestro

### `cliente.py` — Terminal de Acceso
- 🔐 **Validación ciega** — mismo mensaje de error independientemente del tipo de fallo (anti-enumeración)
- 📋 **Agenda personal cifrada en sesión** — datos privados por usuario
- 📝 **Log de accesos** — registro temporal de intentos exitosos y fallidos
- 🚪 **Cierre de sesión** — limpieza completa de la interfaz

<br/>

---

## 📁 Estructura del proyecto

```

-proyecto/
 ├── admin/
 │   ├── admin.py
 │   └── data/          ← cuentas_seguras.json y QR 
 ├── cliente/
 │   ├── cliente.py
 │   └── data/          ← agendas_usuarios.json
 ├── docs/
 │   ├── tarea_modolo8_M_Ciberseguridad.pdf
 │   └── rfc6238.pdf          ← Protocolo RFC6238
-README.md
```

<br/>

---

## 🚀 Instalación y uso

### Requisitos previos

- Python **3.8 o superior**
- Una aplicación TOTP en tu móvil: [Google Authenticator](https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2) · [Authy](https://authy.com/)

### 1. Clonar el repositorio

```bash
git clone https://github.com/ZoneToolsCiber/TOTP-Authentication-System.git
cd TOTP-Authentication-System
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install customtkinter pyotp qrcode pillow
```

### 4. Ejecutar

```bash
# Primero, siempre el panel de administración
python admin.py

# Una vez configurado un usuario, el cliente
python cliente.py
```

<br/>

---

## 🔄 Flujo de ejecución

```
1. python admin.py
   │
   ├── Primera ejecución: genera Token Maestro del admin
   │   └── Escanear QR maestro con Google Authenticator
   │
   ├── Menú principal → "+ REGISTRO AVANZADO DE USUARIO"
   │   ├── Introduce nombre/email del usuario
   │   ├── Configura: algoritmo, intervalo, dígitos, ventana
   │   └── Se genera secreto aleatorio y se guarda en JSON
   │
   └── Seleccionar usuario → "AUDITAR Y VER QR"
       ├── El sistema solicita el Token Maestro actual
       ├── Verificación exitosa → muestra ficha técnica completa
       └── Se genera el QR para entregar al usuario ← ─ ─ ─ ─ ─ ─┐
                                                                   │
2. Usuario escanea el QR con Google Authenticator               escanea
                                                                   │
3. python cliente.py                                               │
   │                                                               │
   ├── Introduce identificador de usuario                          │
   ├── Introduce código TOTP actual (ej. Google Auth) ─ ─ ─ ─ ─ ─ ─┘
   └── Acceso concedido → Agenda personal disponible
```

<br/>

---

## ⚙️ Parámetros técnicos (RFC 6238)

Uno de los aspectos más didácticos del proyecto es que expone todos los parámetros del estándar de forma configurable. Esto permite entender qué hace cada uno en lugar de quedarse con los valores por defecto:

| Parámetro | Variable en código | Valores disponibles | Descripción |
|---|---|---|---|
| **Secreto** | `secret` | Base32 aleatorio | Clave compartida generada con `pyotp.random_base32()` |
| **Intervalo** | `interval` | 15 / 30 / 60 / 90 s | Ventana de validez de cada código |
| **Dígitos** | `digits` | 6 / 8 | Longitud del código OTP generado |
| **Algoritmo** | `algo` / `digest` | SHA-1 / SHA-256 / SHA-512 | Función hash usada en HMAC |
| **Tolerancia** | `window` | 0 / 1 / 2 | Intervalos adyacentes aceptados (compensa desajuste de reloj) |

El parámetro `window` merece especial atención: un valor de `1` significa que el servidor acepta el código del intervalo anterior, el actual y el siguiente. Esto compensa pequeños desajustes entre el reloj del móvil y el del servidor.

<br/>

---

## 🛡️ Seguridad y decisiones de diseño

Estas son las decisiones de diseño más interesantes desde el punto de vista de seguridad, y las razones detrás de cada una:

### Validación ciega (Anti-User Enumeration)

```python
# cliente.py — método validar()
acceso_concedido = False

if user_input in data["usuarios"]:
    # ...verificar TOTP...
    if totp.verify(otp_input, valid_window=u_cfg.get("window", 0)):
        acceso_concedido = True

if acceso_concedido:
    self.mostrar_menu_post_login(user_input)
else:
    self.lbl_info.configure(text="Credenciales inválidas")  # ← siempre el mismo mensaje
```

El sistema **nunca indica si el usuario existe o no**. Un atacante no puede saber si un nombre de usuario está registrado — sólo obtiene "credenciales inválidas" en cualquier caso.

### Token Maestro para auditorías

```python
# admin.py — método verificar_maestro()
admin_s = self.cuentas["admin_master"]["secret"]
if pyotp.totp.TOTP(admin_s).verify(token.strip()):
    self.mostrar_detalles_finales(usuario)
```

El propio administrador necesita su propio TOTP para acceder a los datos de cualquier usuario. Si alguien accede físicamente al equipo del admin, no puede ver los QR sin el móvil del administrador.

### Separación de responsabilidades en los datos

| Archivo | Gestiona | Contiene |
|---|---|---|
| `cuentas_seguras.json` | `admin.py` | Secretos TOTP, parámetros técnicos |
| `agendas_usuarios.json` | `cliente.py` | Datos privados de la agenda |

Un compromiso de la agenda no expone los secretos criptográficos, y viceversa.

<br/>

---

## 📈 Posibles mejoras

El proyecto cumple su objetivo académico, pero en un entorno real estas serían las mejoras prioritarias:

```
🔴 Alta prioridad
├── Cifrado AES-256-GCM para los archivos JSON en reposo
│   └── Los secretos TOTP actualmente se guardan en texto plano
│
🟠 Media prioridad
├── Rate Limiting — límite de intentos de login con bloqueo progresivo
│   └── Actualmente no hay protección contra fuerza bruta en tiempo real
│
🟡 Recomendable
└── Hashing de identificadores de usuario en el JSON
    └── Actualmente los nombres de usuario son visibles en el archivo
```

<br/>

---

## 📚 Recursos para aprender

Si estás empezando en ciberseguridad y quieres entender más sobre este tema, estos son los recursos que me resultaron más útiles:

**Estándares y documentación oficial**
- 📄 [RFC 6238 — TOTP Algorithm](https://datatracker.ietf.org/doc/html/rfc6238) — el estándar completo
- 📄 [RFC 4226 — HOTP Algorithm](https://datatracker.ietf.org/doc/html/rfc4226) — la base de TOTP
- 📄 [NIST SP 800-63B](https://pages.nist.gov/800-63-3/sp800-63b.html) — guía de autenticación digital

**Librerías utilizadas**
- 🐍 [pyotp](https://pyauth.github.io/pyotp/) — documentación oficial
- 📱 [qrcode](https://github.com/lincolnloop/python-qrcode) — generación de QR en Python
- 🎨 [customtkinter](https://customtkinter.tomschimansky.com/) — GUI moderna en Python

**Para entender el contexto**
- 🎥 Busca en YouTube: *"How TOTP works"* — hay explicaciones visuales excelentes
- 📖 El libro *"The Web Application Hacker's Handbook"* tiene un capítulo dedicado a autenticación

<br/>

---

## 📄 Documentación completa

La memoria académica completa del proyecto está disponible en [`proyecto/docs/tarea_modulo8_M_Ciberseguridad.pdf`](proyecto/docs/tarea_modulo8_M_Ciberseguridad.pdf), e incluye fundamentos teóricos del RFC 6238, análisis detallado del código, guía de uso paso a paso y análisis académico de seguridad.

<br/>

---

<div align="center">

**¿Te ha sido útil este proyecto?**  
Si estás en el mismo camino que yo — aprendiendo ciberseguridad y buscando proyectos prácticos que te ayuden a entender los conceptos de verdad — espero que este repositorio te sirva de referencia.

No dudes en abrir un **Issue** si tienes alguna duda, o un **PR** si identificas alguna mejora. Estamos todos aprendiendo.

<br/>

---

*Proyecto académico — Máster en Ciberseguridad*  
*Desarrollado con fines educativos y compartido para la comunidad*

</div>
