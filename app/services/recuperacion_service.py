import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from psycopg.rows import dict_row

from conf.database import obtener_conexion


VIGENCIA_RECUPERACION = timedelta(minutes=15)
INTERVALO_ENTRE_SOLICITUDES = timedelta(seconds=60)


# ESTO NO VA EN EL ENDPOINT POR MOTIVOS DE SEGURIDAD ESTO LLEGA A SALIR EN EL ENDPOINT Y LA SEGURIDAD SE VA DE SABATICO
@dataclass(frozen=True)
class RecuperacionCreada:
    id_recuperacion: int
    correo: str = field(repr=False)
    token: str = field(repr=False)
    fecha_expiracion: datetime


def generar_hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def crear_solicitud_recuperacion(correo: str) -> RecuperacionCreada | None:
    correo_normalizado = correo.strip().lower()

    with obtener_conexion() as conexion:
        with conexion.cursor(row_factory=dict_row) as cursor:
            
            cursor.execute(
                """
                SELECT id_usuario, correo
                FROM usuarios
                WHERE LOWER(correo) = LOWER(%s)
                LIMIT 1
                FOR UPDATE;
                """,
                (correo_normalizado,)
            )
            usuario = cursor.fetchone()

            if usuario is None:
                return None

            # Se usa la hora de la base de datos después de obtener el bloqueo
            cursor.execute(
                """
                SELECT id_recuperacion
                FROM recuperaciones_contrasena
                WHERE id_usuario = %s
                    AND fecha_creacion > statement_timestamp() - %s
                LIMIT 1;
                """,
                (usuario["id_usuario"], INTERVALO_ENTRE_SOLICITUDES)
            )

            if cursor.fetchone() is not None:
                return None

            token = secrets.token_urlsafe(32)
            token_hash = generar_hash_token(token)

            # Solo se invalidan solicitudes anteriores que siguen pendientes
            cursor.execute(
                """
                UPDATE recuperaciones_contrasena
                SET fecha_invalidacion = statement_timestamp()
                WHERE id_usuario = %s
                    AND fecha_uso IS NULL
                    AND fecha_invalidacion IS NULL
                    AND fecha_expiracion > statement_timestamp();
                """,
                (usuario["id_usuario"],)
            )

            cursor.execute(
                """
                INSERT INTO recuperaciones_contrasena (
                    id_usuario,
                    token_hash,
                    fecha_creacion,
                    fecha_expiracion
                )
                VALUES (
                    %s,
                    %s,
                    statement_timestamp(),
                    statement_timestamp() + %s
                )
                RETURNING id_recuperacion, fecha_expiracion;
                """,
                (usuario["id_usuario"], token_hash, VIGENCIA_RECUPERACION)
            )
            solicitud = cursor.fetchone()

            if solicitud is None:
                raise RuntimeError("No fue posible crear la solicitud")

    # El token solo se entrega al código de envío tras confirmar la transacción
    return RecuperacionCreada(
        id_recuperacion=solicitud["id_recuperacion"],
        correo=usuario["correo"],
        token=token,
        fecha_expiracion=solicitud["fecha_expiracion"]
    )
