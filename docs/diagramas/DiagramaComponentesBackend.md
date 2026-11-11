# Componentes del backend — Sistema central SignIA

## Diagrama

<img width="1678" height="602" alt="image" src="https://github.com/user-attachments/assets/443248d1-3dea-46bb-83f7-948193628567" />


## Componentes

| Componente | Módulos en el código |
|---|---|
| Punto de entrada | `app/main.py` |
| Limitador | `app/limiter.py` |
| Rutas de acceso | `app/routes/`: autenticacion, recuperacion_contrasena, restablecimiento_contrasena, usuarios, perfil |
| Rutas de aprendizaje | `app/routes/`: letras, sesiones, resultados, resultados_reconocimiento, progreso, historial, intentos |
| Ruta de visión | `app/routes/vision.py` |
| Seguridad | `app/security.py` |
| Lógica de acceso | `app/services/`: autenticacion, usuarios, recuperacion, restablecimiento |
| Lógica de aprendizaje | `app/services/`: letras, sesiones, intentos, resultados, resultados_reconocimiento, progreso, perfil, historial, aprendizaje |
| Servicio de correo | `app/services/`: correo_recuperacion, microsoft_oauth |
| Repositorio | `app/repositories/aprendizaje_repository.py` |
| Servicio de visión | `app/services/vision_service.py` |
| Motor de visión | `app/vision/` |
| Esquemas | `src/schemas/` |
| Configuración | `conf/`: database, config, logging_config |

Descartados por ser detalles internos: CORS, StaticFiles y manejador de errores de `main.py`.

## Dependencias (origen → destino)

| Origen | Destino | Interfaz | Respaldo |
|---|---|---|---|
| Punto de entrada | Rutas de acceso | `include_router` | `main.py` |
| Punto de entrada | Rutas de aprendizaje | `include_router` | `main.py` |
| Punto de entrada | Ruta de visión | `include_router` | `main.py` |
| Punto de entrada | Limitador | `limiter` | `main.py` |
| Punto de entrada | Configuración | `configurar_logging` | `main.py` |
| Punto de entrada | Servicio de visión | `cerrar_detectores` | `main.py` |
| Rutas de acceso | Limitador | `limiter` | `routes/autenticacion.py` |
| Rutas de acceso | Seguridad | `crear_token_acceso`, `obtener_usuario_actual`, `requerir_administrador`, `revocar_token` | `routes/autenticacion.py`, `usuarios.py`, `perfil.py` |
| Rutas de acceso | Lógica de acceso | `autenticar_usuario`, `crear_usuario`, `crear_solicitud_recuperacion`, `restablecer_contrasena`, `cambiar_rol` | `routes/autenticacion.py`, `usuarios.py`, `recuperacion_contrasena.py`, `restablecimiento_contrasena.py` |
| Rutas de acceso | Lógica de aprendizaje | `consultar_resumen_progreso_usuario`, `obtener_progreso_usuario` | `routes/usuarios.py`, `perfil.py` |
| Rutas de acceso | Servicio de correo | `enviar_correo_recuperacion` | `routes/recuperacion_contrasena.py` |
| Rutas de acceso | Esquemas | modelos Pydantic | `routes/autenticacion.py`, `usuarios.py`, `perfil.py`, etc. |
| Rutas de aprendizaje | Seguridad | `obtener_usuario_actual`, `requerir_administrador` | `routes/letras.py`, `sesiones.py`, `progreso.py`, etc. |
| Rutas de aprendizaje | Lógica de aprendizaje | funciones de cada `*_service` | cada route de aprendizaje |
| Rutas de aprendizaje | Esquemas | modelos Pydantic | cada route de aprendizaje |
| Ruta de visión | Servicio de visión | `procesar_imagen_base64` | `routes/vision.py` |
| Ruta de visión | Esquemas | `VisionEntrada`, `VisionRespuesta` | `routes/vision.py` |
| Seguridad | Lógica de acceso | `obtener_usuario_por_id` | `security.py` |
| Seguridad | Configuración | `obtener_conexion` | `security.py` |
| Lógica de acceso | Configuración | `obtener_conexion` | `services/autenticacion_service.py`, `usuarios_service.py`, etc. |
| Lógica de aprendizaje | Configuración | `obtener_conexion`, `obtener_minimo_aciertos` | `services/aprendizaje_service.py`, etc. |
| Lógica de aprendizaje | Repositorio | `contar_aciertos_letra`, `registrar_aprendizaje` | `services/aprendizaje_service.py` |
| Servicio de visión | Motor de visión | `GestorDetectores`, `reconocer_mano` | `services/vision_service.py` |
| Servicio de correo | Microsoft Graph (externo) | HTTPS/JSON, OAuth 2.0 | `services/correo_recuperacion_service.py`, `microsoft_oauth_service.py` |
| Configuración | Base de datos (externo) | SQL, psycopg | `conf/database.py` |
| Aplicación web (externo) | Rutas de acceso, aprendizaje y visión | REST/JSON, JWT | diagrama de contenedores |
