# Base de datos de SignIA

Se encuentra la estructura inicial de la base de datos de SignIA. Para su desarrollo se utilizó PostgreSQL y, durante las pruebas, la base fue alojada en Neon.

Su función es almacenar la información necesaria para el funcionamiento de la aplicación: los usuarios registrados, las letras del alfabeto LSC, las sesiones de reconocimiento, los resultados obtenidos y el progreso de cada usuario.

## ¿Qué información se almacena?

La base de datos está compuesta por cinco tablas:

- `usuarios`: guarda la información de las cuentas y el rol de cada persona.
- `letras`: contiene las letras disponibles, su descripción y la ruta de su representación visual.
- `sesiones_reconocimiento`: registra cada sesión de práctica iniciada por un usuario.
- `resultados_reconocimiento`: almacena los resultados producidos durante una sesión.
- `progreso_usuario`: permite llevar el seguimiento de los intentos y aciertos de cada usuario por letra.

El diagrama completo y las relaciones entre estas tablas se pueden consultar en [diagrama-er.md](diagrama-er.md).

## Archivos disponibles

Dentro del proyecto se incluyen los siguientes archivos:

- `schema.sql`: contiene la creación de las tablas, claves y restricciones.
- `seed.sql`: contiene datos ficticios para probar las relaciones.
- `diagrama-er.md`: muestra el diagrama entidad-relación.
- `scripts/test_db_connection.py`: permite comprobar la conexión con PostgreSQL.
- `.env.example`: sirve como guía para crear el archivo con la conexión.

## Antes de comenzar

Para ejecutar la base de datos es necesario contar con:

- PostgreSQL o, por lo menos, el cliente `psql`.
- Python 3.12.
- Las dependencias incluidas en `requirements.txt`.
- Una base de datos PostgreSQL. En este proyecto se utilizó Neon.

## Preparación del proyecto

Primero se debe crear un entorno virtual para instalar las dependencias sin afectar otras instalaciones de Python.

En Linux:

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
```

En Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

Después se instalan las dependencias:

```bash
uv pip install -r requirements.txt
```

Si no se utiliza `uv`, también se puede ejecutar:

```bash
pip install -r requirements.txt
```

## Configuración de la conexión

La conexión se configura en un archivo `.env`. Para crearlo, se puede copiar la plantilla incluida en el repositorio.

En Linux:

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Dentro del archivo se debe colocar la cadena de conexión suministrada por Neon:

```env
DATABASE_URL=postgresql://usuario:contrasena@servidor/base_de_datos
```

Esta información es privada. Por esa razón, el archivo `.env` está ignorado por Git y no debe subirse al repositorio.

Para comprobar que la conexión funciona, se ejecuta:

```bash
python scripts/test_db_connection.py
```

Si la configuración es correcta, la terminal mostrará un mensaje de conexión exitosa y las tablas encontradas.

## Creación de las tablas

Para crear la base de datos desde cero, primero hay que conectarse a PostgreSQL mediante `psql`:

```bash
psql "CADENA_DE_CONEXION"
```

Una vez dentro de `psql`, se ejecuta:

```sql
\i database/schema.sql
```

El archivo creará las cinco tablas junto con sus claves primarias, claves foráneas y demás restricciones. Si alguna tabla ya existe, el script no intentará crearla nuevamente.

Para revisar las tablas disponibles se utiliza:

```sql
\dt
```

## Datos de prueba

El archivo `seed.sql` agrega información ficticia para comprobar que las tablas se relacionan correctamente. Incluye dos usuarios, dos letras, una sesión de reconocimiento, dos resultados y dos registros de progreso.

Se puede ejecutar desde la carpeta principal del proyecto con:

```bash
psql "CADENA_DE_CONEXION" -v ON_ERROR_STOP=1 -f database/seed.sql
```

El archivo está preparado para que pueda ejecutarse más de una vez sin duplicar los datos principales. Las contraseñas incluidas son únicamente textos de prueba y no deben utilizarse para iniciar sesión.

Para consultar cuántos registros tiene cada tabla, se pueden usar las siguientes instrucciones:

```sql
SELECT COUNT(*) FROM usuarios;
SELECT COUNT(*) FROM letras;
SELECT COUNT(*) FROM sesiones_reconocimiento;
SELECT COUNT(*) FROM resultados_reconocimiento;
SELECT COUNT(*) FROM progreso_usuario;
```

## Validaciones incluidas

La estructura fue diseñada para mantener la consistencia de la información. Entre las validaciones más importantes se encuentran las siguientes:

- Cada usuario debe tener un correo diferente.
- No se puede crear una sesión para un usuario que no exista.
- No se puede guardar un resultado sin una sesión existente.
- Los resultados deben utilizar letras registradas en el sistema.
- El progreso debe pertenecer a un usuario y a una letra existentes.
- Un usuario solo puede tener un registro de progreso por cada letra.
- La cantidad de aciertos no puede ser mayor que la cantidad de intentos.
- La confianza generada por el reconocimiento debe estar entre `0` y `1`. Por ejemplo, `0.80` representa una confianza del 80 %.
- Los campos obligatorios no pueden quedar vacíos.

Estas restricciones se comprobaron intentando insertar sesiones, resultados y progresos relacionados con registros inexistentes. PostgreSQL rechazó correctamente esas operaciones.

## Consideraciones de seguridad

El frontend no debe conectarse directamente con PostgreSQL. La comunicación se realizará de la siguiente manera:

**Frontend → Backend → Base de datos**

La cadena `DATABASE_URL` será utilizada únicamente por el backend. Además, cuando se implemente el registro de usuarios, las contraseñas deberán almacenarse de forma cifrada mediante un hash seguro.

Nunca se deben publicar archivos `.env`, contraseñas o cadenas de conexión en GitHub.