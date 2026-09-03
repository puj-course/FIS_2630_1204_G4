# Pruebas del flujo completo del perfil

## Objetivo

Validar el flujo desde la pantalla de perfil hasta la consulta de la información almacenada en PostgreSQL, comprobando que los datos mostrados correspondan únicamente al usuario autenticado.

## Entorno de prueba

* Frontend: React y Vite en `http://localhost:5173`.
* Backend: FastAPI en `http://127.0.0.1:8000`.
* Base de datos: PostgreSQL alojada en Neon.
* Usuario utilizado: cuenta creada exclusivamente para las pruebas del perfil.

## Pruebas automatizadas

Se ejecutó:

```bash
python -m unittest src.tests.test_perfil -v
```

Resultado:

```text
Ran 7 tests

OK
```

Las pruebas verificaron:

* Rechazo de solicitudes sin autenticación.
* Rechazo de usuarios inexistentes.
* Consulta de la información del usuario autenticado.
* Protección frente al envío de identificadores de otros usuarios.
* Respuesta válida para usuarios sin progreso.
* Cálculo del porcentaje de avance.
* Manejo de errores al consultar la base de datos.

## Pruebas del flujo completo

| Caso                        | Resultado esperado                                    | Resultado obtenido                                                           | Estado   |
| --------------------------- | ----------------------------------------------------- | ---------------------------------------------------------------------------- | -------- |
| Registro e inicio de sesión | El usuario puede registrarse e ingresar               | El registro y el inicio de sesión finalizaron correctamente                  | Aprobado |
| Consulta del perfil         | Se muestra el nombre y correo del usuario autenticado | La información mostrada coincidió con la cuenta utilizada                    | Aprobado |
| Usuario sin progreso        | El perfil muestra un porcentaje inicial de `0%`       | Se mostró `0.00%`, con todos los indicadores de avance en cero               | Aprobado |
| Usuario con progreso        | El porcentaje coincide con las letras dominadas       | Con 1 de 2 letras dominadas se mostró `50.00%`                               | Aprobado |
| Estadísticas de avance      | Se muestran los valores almacenados en PostgreSQL     | Se mostraron 1 letra iniciada, 1 dominada, 4 intentos y 3 aciertos           | Aprobado |
| Comunicación con el backend | La consulta responde sin errores                      | `GET /perfil` respondió con estado `200 OK`                                  | Aprobado |
| Separación entre usuarios   | La consulta utiliza el usuario asociado al JWT        | El endpoint ignoró identificadores externos y utilizó el usuario autenticado | Aprobado |

## Verificación en PostgreSQL

Se confirmó que el usuario de prueba estaba almacenado correctamente y que inicialmente no tenía registros en `progreso_usuario`.

Posteriormente se agregó un registro de progreso para una de las dos letras activas. Al recargar el perfil, el frontend mostró un avance de `50.00%`, correspondiente al cálculo:

```text
1 letra dominada / 2 letras activas × 100 = 50%
```

## Problemas encontrados

No se encontraron errores funcionales durante el flujo completo.

Durante las pruebas automatizadas aparecieron advertencias relacionadas con dependencias de pruebas y con la longitud de la clave JWT utilizada únicamente en el entorno de prueba. Estas advertencias no causaron fallos y las siete pruebas finalizaron correctamente.

## Conclusión

El perfil consulta correctamente la información del usuario autenticado desde PostgreSQL. El nombre, el correo, las estadísticas y el porcentaje de progreso coinciden con los datos almacenados. Además, los usuarios sin avance reciben un porcentaje inicial válido y las solicitudes completan el recorrido entre frontend, backend y base de datos sin errores.
