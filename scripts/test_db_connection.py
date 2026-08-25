import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

url_base_datos = os.getenv("DATABASE_URL")

if not url_base_datos:
    print("No se encontró DATABASE_URL en el archivo .env.")
else:
    try:
        conexion = psycopg.connect(url_base_datos)
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)

        tablas = cursor.fetchall()

        print("Conexión exitosa con Neon.")
        print("Tablas encontradas:")

        for tabla in tablas:
            print("-", tabla[0])

        cursor.close()
        conexion.close()

    except Exception as error:
        print("No fue posible conectarse a la base de datos.")
        print(error)