import os

import psycopg
from dotenv import load_dotenv


load_dotenv()


def obtener_conexion():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError(
            "No se encontró DATABASE_URL en el archivo .env"
        )

    return psycopg.connect(database_url)