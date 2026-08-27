import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

from app.services.autenticacion_service import obtener_usuario_por_id


load_dotenv()

ALGORITMO_JWT = "HS256"

seguridad_bearer = HTTPBearer(auto_error=False)


def obtener_clave_jwt():
    clave = os.getenv("JWT_SECRET")

    if not clave:
        raise RuntimeError(
            "No se encontró JWT_SECRET en el archivo .env"
        )

    return clave


def obtener_minutos_expiracion():
    valor = os.getenv("JWT_EXPIRE_MINUTES", "60")

    try:
        return int(valor)
    except ValueError as error:
        raise RuntimeError(
            "JWT_EXPIRE_MINUTES debe ser un número entero"
        ) from error


def crear_token_acceso(id_usuario: int):
    momento_actual = datetime.now(timezone.utc)
    fecha_expiracion = momento_actual + timedelta(
        minutes=obtener_minutos_expiracion()
    )

    contenido = {
        "sub": str(id_usuario),
        "iat": momento_actual,
        "exp": fecha_expiracion
    }

    return jwt.encode(
        contenido,
        obtener_clave_jwt(),
        algorithm=ALGORITMO_JWT
    )


def crear_error_credenciales():
    return HTTPException(
        status_code=401,
        detail="No fue posible validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"}
    )


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(
        seguridad_bearer
    )
):
    if credenciales is None:
        raise crear_error_credenciales()

    try:
        contenido = jwt.decode(
            credenciales.credentials,
            obtener_clave_jwt(),
            algorithms=[ALGORITMO_JWT]
        )

        id_usuario = int(contenido.get("sub"))

    except (InvalidTokenError, TypeError, ValueError):
        raise crear_error_credenciales()

    usuario = obtener_usuario_por_id(id_usuario)

    if usuario is None:
        raise crear_error_credenciales()

    return usuario