# Base de datos del backend de SignIA

## Descripción general

SignIA utiliza PostgreSQL para almacenar las cuentas, el alfabeto LSC, las sesiones de reconocimiento y la información que permite consultar los resultados y el aprendizaje de cada usuario. La conexión se configura mediante `DATABASE_URL` y se realiza desde el backend con Psycopg. El proyecto puede utilizar una base PostgreSQL local o una base alojada externamente, como Neon, siempre que la cadena de conexión sea válida.

## Tablas actuales

En la versión revisada se encontraron **ocho tablas**, considerando `database/schema.sql` y las migraciones de intentos:

| Tabla | Información almacenada |
|---|---|
| `usuarios` | Cuentas, contraseñas con hash, roles, estado y control de intentos fallidos |
| `letras` | Letras del alfabeto LSC, descripción y ruta de imagen |
| `sesiones_reconocimiento` | Sesiones de práctica y sus estados |
| `resultados_reconocimiento` | Letra objetivo, letra detectada, confianza y resultado de cada reconocimiento registrado |
| `progreso_usuario` | Estado de aprendizaje por usuario y letra, intentos y aciertos |
| `intentos_reconocimiento` | Intentos asociados a usuarios, sesiones, letras y resultados |
| `recuperaciones_contrasena` | Solicitudes de recuperación, token almacenado como hash y fechas de validez |
| `tokens_revocados` | Identificadores de tokens de sesión revocados |

Las relaciones se establecen con claves foráneas. Por ejemplo, cada sesión pertenece a un usuario, cada resultado se relaciona con su sesión y las letras correspondientes, y el progreso identifica la pareja usuario-letra. La tabla de intentos tiene una restricción para que un resultado genere como máximo un intento asociado. El esquema también valida estados permitidos, valores de confianza y el orden de varias fechas.

## Archivos de base de datos

En `database/` se encuentran los siguientes archivos:

- `schema.sql`: crea las tablas principales, incluidas las de recuperación de contraseña y revocación de tokens.
- `migrations/intentos_reconocimiento.sql`: crea la tabla de intentos.
- `migrations/agregar_resultado_a_intentos.sql`: vincula cada intento con su resultado y evita duplicar la relación.
- `migrations/recuperaciones_contrasena.sql`: contiene una creación de la tabla de recuperación que actualmente también figura en el esquema principal; no debe ejecutarse sin revisar si la tabla ya existe.
- `seed.sql`: agrega datos iniciales de prueba.
- `diagrama-er.md`: contiene la documentación del diagrama entidad-relación.
- `scripts/test_db_connection.py`: comprueba una conexión y muestra las tablas encontradas.

## Crear la base de datos manualmente

Con PostgreSQL preparado y una cadena de conexión disponible, desde la raíz del proyecto se pueden ejecutar los archivos SQL en el siguiente orden:

```bash
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/schema.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/migrations/intentos_reconocimiento.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/migrations/agregar_resultado_a_intentos.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f database/seed.sql
```

Los scripts de migración de intentos están pensados para aplicarse sobre una base que todavía no tenga esa tabla ni sus columnas. Antes de volver a ejecutarlos sobre una base existente hay que revisar su estado, porque contienen operaciones de creación y modificación que pueden fallar si ya fueron aplicadas.

## Inicialización mediante Docker Compose

El archivo `docker-compose.yml` define el servicio PostgreSQL con la imagen `postgres:16`, un volumen persistente y montajes de los SQL de inicialización. Cuando el volumen de datos está vacío, PostgreSQL ejecuta los archivos montados en `/docker-entrypoint-initdb.d/` según su nombre y crea la base de prueba. Esos scripts no se vuelven a ejecutar automáticamente al reiniciar un contenedor que ya tiene su volumen inicializado.

Para utilizar la base de datos del contenedor, una configuración local del backend puede tener una dirección como esta, con credenciales de prueba que deben coincidir con las definidas para PostgreSQL:

```dotenv
POSTGRES_USER=signia
POSTGRES_PASSWORD=CAMBIAR_POR_CLAVE_DE_PRUEBA
POSTGRES_DB=signia
DATABASE_URL=postgresql://signia:CAMBIAR_POR_CLAVE_DE_PRUEBA@postgres:5432/signia
```

En este ejemplo `postgres` es el nombre del servicio dentro de la red de Docker. **Al ejecutar el backend directamente en el computador**, la dirección debe apuntar a la ubicación accesible desde ese computador, como `localhost` cuando corresponda.

## Conexión y seguridad

La cadena `DATABASE_URL` se guarda en el archivo `.env`, que no debe publicarse. También deben mantenerse fuera del repositorio las contraseñas y los tokens. Las consultas a la base de datos se realizan desde los servicios del backend y no directamente desde el frontend. Para verificar la conexión se puede ejecutar `python scripts/test_db_connection.py`, que imprime las tablas accesibles por la cuenta configurada.

El diagrama del proyecto está en [`database/diagrama-er.md`](../database/diagrama-er.md). Para preparar el entorno completo puede consultarse [installation_backend.md](installation_backend.md).
