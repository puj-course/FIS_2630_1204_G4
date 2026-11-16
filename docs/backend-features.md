# Funcionalidades del backend de SignIA

## Descripción general

El backend de SignIA administra la información de los usuarios, el alfabeto de la Lengua de Señas Colombiana, las sesiones de práctica y el progreso de aprendizaje. También recibe las imágenes enviadas para reconocimiento visual y conserva los resultados que se registran durante las prácticas. Las funcionalidades descritas corresponden a los archivos presentes en la rama `develop` revisada.

## Autenticación y cuentas

Las rutas de `app/routes/autenticacion.py` permiten el autorregistro de usuarios, el inicio de sesión, la consulta de la cuenta autenticada y el cierre de sesión. El acceso se controla con tokens JWT, y el cierre de sesión guarda la revocación correspondiente. El proceso de inicio de sesión aplica un límite de solicitudes por IP y contempla el bloqueo temporal de una cuenta después de intentos fallidos.

También se encuentran implementadas las solicitudes de recuperación y restablecimiento de contraseña. El sistema genera solicitudes temporales, utiliza un token para el enlace de recuperación y administra el envío por correo desde los servicios correspondientes. Para utilizar ese flujo se requiere configurar el método de envío.

## Administración de usuarios

Los administradores pueden registrar usuarios con un rol, consultar el listado, buscar cuentas, cambiar roles, desactivar usuarios y reactivarlos. También pueden consultar el resumen de progreso de una cuenta. Estas acciones se encuentran en `app/routes/usuarios.py` y requieren la validación del rol administrativo.

## Letras y perfil

El módulo de letras permite consultar el alfabeto registrado, obtener la información de una letra y actualizar su descripción o ruta de imagen cuando quien realiza el cambio es un administrador. El backend también publica los recursos de imágenes mediante `/assets`.

Cada usuario autenticado puede consultar su perfil, que reúne nombre, correo, rol y un resumen de aprendizaje. Ese resumen permite conocer el número de letras trabajadas, las aprendidas y el porcentaje de progreso.

## Sesiones de reconocimiento e historial

El sistema permite iniciar sesiones, consultar las sesiones propias y finalizarlas. Para registrar resultados en una sesión activa, se verifica que la sesión pertenezca al usuario y que las letras indicadas existan. Después se guarda la respuesta y se calcula si coincide con la letra objetivo. También están disponibles las consultas de resultados por sesión, de intentos con filtros y del historial de reconocimiento del usuario.

El proyecto conserva un segundo grupo de rutas bajo `/resultados-reconocimiento`, que permite registrar un resultado creando una sesión finalizada, consultar los resultados propios y eliminarlos. Este flujo debe distinguirse del registro de resultados en una sesión activa, porque su implementación es diferente.

## Aprendizaje y progreso

El backend guarda el estado de las letras del usuario y permite consultar o modificar el progreso. En el flujo de `POST /resultados`, cada registro correcto también genera un intento y desencadena la evaluación del aprendizaje. La regla predeterminada requiere tres aciertos acumulados para una letra, aunque puede configurarse por medio de `APRENDIZAJE_MIN_ACIERTOS`.

Los aciertos se consultan por usuario y letra, incluso cuando corresponden a distintas sesiones. El servicio marca la letra como aprendida cuando se alcanza el mínimo, sin duplicar el registro. La lógica se encuentra en `app/services/aprendizaje_service.py` y `app/repositories/aprendizaje_repository.py`.

## Reconocimiento visual

La ruta `POST /vision/reconocer` recibe una imagen codificada en Base64. El servicio comprueba su tamaño y formato, utiliza OpenCV para decodificarla y delega en el módulo de visión la detección de la mano y el reconocimiento. Existen dos modalidades: una para letras estáticas y otra para letras que requieren movimiento, esta última utiliza una secuencia de fotogramas cuando se proporciona su identificador.

La detección se administra mediante un gestor compartido de detectores y el reconocimiento selecciona una estrategia según el modo solicitado. El código también mide y registra el tiempo de algunas operaciones de reconocimiento. La respuesta informa la letra encontrada o indica que no pudo reconocerse una letra.

## Seguridad y organización del código

La autenticación utiliza JWT y contraseñas almacenadas mediante hash. Las rutas revisan el usuario autenticado y aplican permisos cuando corresponde. El proyecto separa sus endpoints en `app/routes/`, la lógica de las operaciones en `app/services/`, los esquemas de entrada y salida en `src/schemas/` y la conexión con PostgreSQL en `conf/database.py`.

## Verificación

La API publica su documentación en `http://localhost:8000/docs`. Las pruebas automatizadas del backend están en `src/tests/` y el workflow `backend-ci.yml` ejecuta Ruff y pytest con cobertura. Los endpoints exactos se pueden consultar en [api.md](api.md), y el funcionamiento del reconocimiento en [endpoint-vision.md](endpoint-vision.md).
