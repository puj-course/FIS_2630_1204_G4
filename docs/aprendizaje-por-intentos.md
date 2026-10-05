# Aprendizaje de letras mediante intentos exitosos

## Historia de usuario

HU #37 — Determinar letras aprendidas mediante cantidad de intentos exitosos.

Issue principal: #365.

Subissues:
- #366: definir las condiciones de aprendizaje.
- #367: implementar el servicio de validación del aprendizaje.
- #368: integrar la evaluación después del registro de intentos.
- #369: validar el aprendizaje automático.

## Condición de aprendizaje

Una letra se considera aprendida cuando el usuario alcanza el mínimo
configurado de intentos correctos para esa letra.

El valor predeterminado es de tres aciertos acumulados. Este valor es
una decisión de implementación y puede modificarse mediante configuración.

Los aciertos:
- Se cuentan por usuario y letra.
- Pueden pertenecer a distintas sesiones del mismo usuario.
- No necesitan ser consecutivos.
- Incluyen los intentos históricos almacenados.

Los intentos incorrectos no suman aciertos ni reinician el conteo.

## Configuración

La variable APRENDIZAJE_MIN_ACIERTOS establece el mínimo requerido.

Ejemplo en el archivo .env de la raíz del proyecto:

```dotenv
APRENDIZAJE_MIN_ACIERTOS=3
```

Si la variable no está definida, se utiliza 3.

Solo se aceptan enteros mayores que cero. Un valor vacío, cero, negativo
o no entero genera ConfiguracionAprendizajeError.

Después de modificar el archivo .env, se debe reiniciar el backend para
cargar la configuración. Una variable definida en el entorno tiene
prioridad sobre el valor del archivo .env.

## Flujo automático

1. El servicio de resultados valida la sesión, su propietario y las letras.
2. Guarda el resultado y su intento dentro de la misma transacción.
3. Confirma esa transacción.
4. Si el resultado es correcto, solicita la evaluación del aprendizaje.
5. El servicio de aprendizaje consulta los aciertos almacenados.
6. Si se alcanza el mínimo, registra la letra como aprendida.

El usuario evaluado se obtiene de la sesión y la letra corresponde
a la letra objetivo del resultado correcto.

Un resultado incorrecto se almacena con su intento, pero no activa
la evaluación del aprendizaje.

## Responsabilidades

- conf/config.py: carga y valida el mínimo de aciertos.
- app/repositories/aprendizaje_repository.py: cuenta aciertos y registra
  nuevos aprendizajes en PostgreSQL.
- app/services/aprendizaje_service.py: aplica la condición de aprendizaje.
- app/services/resultados_service.py: solicita la evaluación después
  de confirmar el resultado y el intento.

El servicio de aprendizaje utiliza los intentos almacenados y puede
funcionar sin ejecutar el módulo visual. Recibe identificadores previamente
validados por el flujo de resultados.

## Persistencia y repeticiones

El aprendizaje se almacena en progreso_usuario con dominada = TRUE.

La restricción única sobre id_usuario e id_letra evita registros duplicados.
Si existe un registro pendiente, se actualiza a aprendido.

Si la letra ya está aprendida, la evaluación automática no modifica
el registro ni su fecha de actualización.

El conteo para decidir el aprendizaje se obtiene de intentos_reconocimiento.
Esta implementación no recalcula los campos cantidad_intentos,
cantidad_aciertos ni fecha_ultima_practica de progreso_usuario.

## Cambios del mínimo

Cada evaluación utiliza el mínimo configurado en ese momento.

Aumentar el mínimo no elimina aprendizajes anteriores.
Cambiar la configuración no ejecuta un procesamiento masivo del historial.
Las letras pendientes se evalúan cuando ocurre un nuevo reconocimiento
correcto, considerando los aciertos que ya están almacenados.

## Manejo de errores

La evaluación del aprendizaje utiliza una transacción independiente
de la que guarda el resultado y el intento.

Si falla la evaluación:
- El error se registra en los logs.
- El resultado y su intento permanecen almacenados.
- El resultado puede devolverse correctamente al cliente.

No existe un reintento inmediato automático. Un nuevo reconocimiento
correcto vuelve a evaluar los aciertos acumulados.

Si falla el guardado del resultado, del intento o su confirmación,
no se ejecuta la evaluación del aprendizaje.

## Porcentaje de progreso

El perfil calcula:

porcentaje = letras activas aprendidas × 100 / total de letras activas

El resultado se redondea a dos decimales. Si no hay letras activas,
el porcentaje es 0.

Los aciertos que todavía no alcanzan el mínimo no aumentan el porcentaje.
Repetir una letra aprendida tampoco aumenta el número de letras dominadas.

## Validaciones realizadas

Se probaron:
- El mínimo predeterminado y otros valores positivos.
- El rechazo de configuraciones inválidas.
- El aprendizaje al alcanzar el mínimo.
- La independencia entre usuarios y entre letras.
- La acumulación de aciertos entre sesiones.
- Los errores intercalados entre aciertos.
- La conservación de letras aprendidas al aumentar el mínimo.
- La ausencia de duplicados y cambios innecesarios en el progreso.
- El orden entre confirmación del resultado y evaluación.
- La conservación de resultados e intentos ante errores de aprendizaje.
- La recuperación mediante un reconocimiento posterior.
- El porcentaje consultado mediante el endpoint /perfil.

Las pruebas de integración utilizan PostgreSQL mediante DATABASE_URL.
Crean usuarios de prueba y eliminan sus datos al finalizar.

## Comando de validación

Desde la raíz del proyecto, con el entorno virtual activo:

```bash
python -m pytest src/tests/test_aprendizaje_service.py src/tests/test_resultados_service.py src/tests/test_resultados_progreso_integracion.py src/tests/test_endpoint_resultados_integracion.py -v
```