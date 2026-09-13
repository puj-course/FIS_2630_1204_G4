# Funcionalidades implementadas del Backend

## Descripción general

El backend contiene los servicios necesarios para gestionar
usuarios, autenticación, información del alfabeto LSC, recuperación de
contraseña, perfil de usuario y procesamiento de información relacionada
con visión computacional.

La arquitectura utiliza una separación entre rutas y servicios, donde
las rutas reciben las solicitudes HTTP y delegan la lógica de negocio a
los servicios correspondientes.

------------------------------------------------------------------------

# Autenticación

## Inicio de sesión

Endpoint:

POST /auth/login

Permite que un usuario registrado pueda iniciar sesión utilizando su
correo y contraseña.

Proceso:

1.  Recibe las credenciales del usuario.
2.  Valida la información mediante el servicio de autenticación.
3.  Genera un token JWT si las credenciales son correctas.
4.  Retorna el token y la información básica del usuario.

------------------------------------------------------------------------

## Registro de usuarios

Endpoint:

POST /auth/registro

Permite que un usuario pueda registrarse en el sistema.

Características:

-   Crea usuarios con rol usuario.
-   Valida que el correo no esté registrado.
-   Retorna la información del usuario creado.

------------------------------------------------------------------------

## Consulta de usuario autenticado

Endpoint:

GET /auth/me

Permite consultar la información del usuario actualmente autenticado
mediante un token JWT válido.

------------------------------------------------------------------------

# Gestión de usuarios

## Registro administrativo de usuarios

Endpoint:

POST /usuarios

Permite a un administrador registrar nuevos usuarios dentro del sistema.

Características:

-   Requiere permisos administrativos.
-   Permite definir el rol del usuario.
-   Valida correos existentes.

------------------------------------------------------------------------

# Módulo de letras LSC

El módulo de letras permite gestionar la información almacenada del
alfabeto de Lengua de Señas Colombiana.

------------------------------------------------------------------------

## Consultar letras registradas

Endpoint:

GET /letras

Obtiene todas las letras disponibles en la base de datos.

La respuesta incluye información como:

-   Identificador de la letra.
-   Letra.
-   Descripción.
-   Información visual asociada.

------------------------------------------------------------------------

## Consultar una letra específica

Endpoint:

GET /letras/{id_letra}

Permite consultar la información de una letra específica mediante su
identificador.

------------------------------------------------------------------------

## Actualizar información de una letra

Endpoint:

PATCH /letras/{id_letra}

Permite actualizar información de una letra.

Características:

-   Disponible únicamente para administradores.
-   Permite actualizar campos específicos.
-   Valida que exista información para modificar.

------------------------------------------------------------------------

# Perfil de usuario

## Consulta de perfil

Endpoint:

GET /perfil

Permite consultar la información personal y progreso del usuario
autenticado.

Incluye:

-   Identificador del usuario.
-   Nombre.
-   Correo.
-   Rol.
-   Progreso dentro del sistema.

------------------------------------------------------------------------

# Recuperación de contraseña

El sistema cuenta con un flujo de recuperación de contraseña mediante
correo electrónico.

------------------------------------------------------------------------

## Solicitar recuperación

Endpoint:

POST /recuperar-contrasena

Permite solicitar instrucciones para recuperar una contraseña.

Proceso:

1.  El usuario envía su correo.
2.  Se genera una solicitud de recuperación.
3.  Se crea un token temporal.
4.  Se envían instrucciones mediante correo electrónico.

Características:

-   La respuesta no revela si el correo existe por motivos de seguridad.
-   Las solicitudes tienen tiempo de expiración.
-   Se evita generar múltiples solicitudes en poco tiempo.

------------------------------------------------------------------------

# Restablecimiento de contraseña

Endpoint:

POST /restablecer-contrasena

Permite establecer una nueva contraseña utilizando un token válido.

Características:

-   Valida la vigencia del token.
-   Verifica la confirmación de contraseña.
-   Actualiza la contraseña almacenada.
-   Informa cuando la actualización fue exitosa.

------------------------------------------------------------------------

# Seguridad

El backend implementa mecanismos de seguridad para proteger información
sensible.

Incluye:

-   Autenticación mediante JWT.
-   Validación de usuarios autenticados.
-   Control de permisos administrativos.
-   Manejo seguro de tokens de recuperación.

------------------------------------------------------------------------

# Procesamiento visual

El backend cuenta con un módulo de visión computacional integrado
mediante servicios.

Sus responsabilidades incluyen:

-   Comunicación con el módulo visual.
-   Procesamiento de solicitudes relacionadas con reconocimiento.
-   Separación entre lógica visual y endpoints.

Tecnologías utilizadas:

-   OpenCV.
-   MediaPipe.

------------------------------------------------------------------------

# Funcionalidades pendientes

Actualmente algunas funcionalidades continúan en desarrollo:

-   Integración completa del reconocimiento visual con la interfaz del
    usuario.
-   Ampliación del reconocimiento del alfabeto LSC.
-   Nuevas funcionalidades relacionadas con progreso y aprendizaje.
