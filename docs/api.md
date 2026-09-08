# API de SignIA - contrato Frontend / Backend

Esto sale de la HU #35 ("Definir el soporte del backend para las vistas iniciales de SignIA"). La idea es dejar claro qué le pide cada vista al backend, para que frontend y backend puedan avanzar en paralelo sin pisarse. No es la implementación real ni el sistema de auth, eso lo dejamos para las HUs que vienen después (abajo detallo qué queda fuera).

## 1. Lo que ya hay

Antes de inventar nada nuevo, esto es lo que ya corre en el repo:

| Método | Ruta      | Qué hace                                                               | Dónde está               |
| ------ | --------- | ---------------------------------------------------------------------- | ------------------------ |
| GET    | `/health` | Chequeo de que el backend está vivo                                    | directo en `app/main.py` |
| GET    | `/letras` | Trae el alfabeto LSC registrado (para la vista de referencia/práctica) | `app/routes/letras.py`   |

Todo lo demás en este documento es propuesta, y trato de seguir el mismo estilo que ya usaron en `letras` para no inventar un patrón nuevo a mitad de proyecto.

## 2. Qué necesita cada vista

- Inicio: nada obligatorio, es básicamente estática. A futuro capaz conviene saber si hay sesión activa para cambiar el botón de "Iniciar sesión" por "Ir a práctica", pero eso no es parte de esta HU.
- Registro: crear una cuenta, con `POST /auth/registro`.
- Login: validar credenciales y devolver algo de sesión, con `POST /auth/login`.
- Perfil: ver y editar los datos del usuario logueado. `GET /perfil` y `PUT /perfil`.
- Práctica: consultar el alfabeto (ya existe con `/letras`) y guardar el resultado de cada intento. Para eso, `POST /practica/sesiones` y `GET /practica/progreso`.

## 3. Endpoints propuestos

### 3.1 Auth (`app/routes/auth.py`)

#### `POST /auth/registro`

Crea el usuario. Request (`RegistroSolicitud`):

```json
{
  "nombre": "Oscar Martínez",
  "correo": "oscar@example.com",
  "contrasena": "algo-seguro-123"
}
```

Responde 201 con `UsuarioRespuesta`:

```json
{
  "id_usuario": 1,
  "nombre": "Oscar Martínez",
  "correo": "oscar@example.com",
  "fecha_registro": "2026-08-27T10:00:00"
}
```

409 si el correo ya existe, 500 si se cae la base de datos (mismo patrón que ya usa `letras.py`, no hay que reinventar nada acá).

#### `POST /auth/login`

Request (`LoginSolicitud`):

```json
{
  "correo": "oscar@example.com",
  "contrasena": "algo-seguro-123"
}
```

Responde 200 con `LoginRespuesta`:

```json
{
  "token": "jwt-o-similar",
  "usuario": {
    "id_usuario": 1,
    "nombre": "Oscar Martínez",
    "correo": "oscar@example.com"
  }
}
```

401 si las credenciales no coinciden.

Ojo: lo de JWT es una recomendación nomás, todavía no está decidido en firme. Es lo que más se usa con FastAPI y evita tener que guardar sesiones en el server, pero la implementación real (hash de la contraseña con `passlib`/`bcrypt`, armar y validar el token) queda para más adelante.

### 3.2 Perfil (`app/routes/perfil.py`)

#### `GET /perfil`

Requiere estar logueado. Devuelve (`PerfilRespuesta`):

```json
{
  "id_usuario": 1,
  "nombre": "Oscar Martínez",
  "correo": "oscar@example.com",
  "fecha_registro": "2026-08-27T10:00:00",
  "letras_practicadas": 12,
  "porcentaje_acierto": 78.5
}
```

#### `PUT /perfil`

Actualiza lo que se pueda editar. Request (`PerfilActualizacionSolicitud`):

```json
{
  "nombre": "Oscar Eduardo Martínez"
}
```

Responde 200 con el mismo esquema de `GET /perfil`. 401 si no hay sesión válida.

### 3.3 Práctica (`app/routes/practica.py`)

#### `POST /practica/sesiones`

Guarda el resultado de un intento sobre una letra puntual. Request (`PracticaSolicitud`):

```json
{
  "id_letra": 3,
  "acierto": true
}
```

Responde 201 (`PracticaRespuesta`):

```json
{
  "id_sesion": 45,
  "id_letra": 3,
  "acierto": true,
  "fecha": "2026-08-27T10:15:00"
}
```

#### `GET /practica/progreso`

Resumen de progreso del usuario logueado, letra por letra (`ProgresoRespuesta`, lista):

```json
[
  {
    "id_letra": 3,
    "letra": "C",
    "intentos": 8,
    "aciertos": 6
  }
]
```

401 si no hay sesión, 500 siguiendo el mismo patrón que `letras_service.py`.

## 4. Esquemas Pydantic

Copiando el estilo de `src/schemas/letra.py`:

```python
# src/schemas/usuario.py
from datetime import datetime
from pydantic import BaseModel


class RegistroSolicitud(BaseModel):
    nombre: str
    correo: str
    contrasena: str


class LoginSolicitud(BaseModel):
    correo: str
    contrasena: str


class UsuarioRespuesta(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    fecha_registro: datetime


class LoginRespuesta(BaseModel):
    token: str
    usuario: UsuarioRespuesta


class PerfilRespuesta(UsuarioRespuesta):
    letras_practicadas: int
    porcentaje_acierto: float


class PerfilActualizacionSolicitud(BaseModel):
    nombre: str | None = None
```

```python
# src/schemas/practica.py
from datetime import datetime
from pydantic import BaseModel


class PracticaSolicitud(BaseModel):
    id_letra: int
    acierto: bool


class PracticaRespuesta(BaseModel):
    id_sesion: int
    id_letra: int
    acierto: bool
    fecha: datetime


class ProgresoRespuesta(BaseModel):
    id_letra: int
    letra: str
    intentos: int
    aciertos: int
```

## 5. Cómo quedarían organizadas las rutas

Mismo patrón que ya tiene `letras`: router, luego service, luego `conf/database.py`. Sin capa de `controllers/` por ahora; si en algún momento crece mucho la lógica se puede meter después.

```
app/
├── main.py                      # acá se registran los routers nuevos
├── routes/
│   ├── letras.py                # ya existe
│   ├── auth.py                  # nuevo, /auth/registro y /auth/login
│   ├── perfil.py                # nuevo, GET/PUT /perfil
│   └── practica.py              # nuevo, /practica/sesiones y /practica/progreso
└── services/
    ├── letras_service.py        # ya existe
    ├── auth_service.py          # nuevo
    ├── perfil_service.py        # nuevo
    └── practica_service.py      # nuevo

src/schemas/
├── letra.py                     # ya existe
├── usuario.py                   # nuevo
└── practica.py                  # nuevo
```

Y en `app/main.py` solo hay que agregar:

```python
from app.routes.auth import router as auth_router
from app.routes.perfil import router as perfil_router
from app.routes.practica import router as practica_router

app.include_router(auth_router)
app.include_router(perfil_router)
app.include_router(practica_router)
```

## 6. Tablas que van a hacer falta (solo como referencia)

Para que todo esto funcione en serio se van a necesitar tablas `usuarios` y `sesiones_practica`. El diseño del esquema no es parte de esta HU, lo menciono nada más para que quien implemente `auth_service.py` / `practica_service.py` sepa que primero tiene que resolver eso.

## 7. Qué queda fuera de esta HU

No es que se nos haya olvidado, es que decidimos dejarlo para después:

- La implementación real de los endpoints (eso va en las HUs de implementación, ligado a los issues de vistas #52-#55).
- Decidir JWT vs. sesiones en serio, acá solo dejamos la recomendación.
- Hashing y validación de contraseñas.
- El diseño detallado de las tablas.
- Reconocimiento por cámara / MediaPipe, que es el issue #58 y va por separado.

## 8. Config

El backend ya lee `DATABASE_URL` desde un `.env` (revisar `conf/database.py` y `.env.example`). No hace falta ninguna variable nueva para lo que está en este documento. Cuando se meta JWT sí va a hacer falta agregar algo como `JWT_SECRET` en ese mismo `.env`.
