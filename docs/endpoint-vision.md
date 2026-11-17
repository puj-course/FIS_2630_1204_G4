# Endpoint de reconocimiento visual

## Objetivo

El endpoint permite enviar una imagen al backend para reconocer una letra del alfabeto LSC a partir de la mano detectada. La implementación actual permite seleccionar entre reconocimiento estático y reconocimiento con movimiento. El procesamiento se realiza en `app/routes/vision.py`, `app/services/vision_service.py` y `app/vision/`.

## Ruta

```http
POST /vision/reconocer
Content-Type: application/json
```

La solicitud no exige un token de autenticación en el código de la ruta revisada.

## Datos de entrada

```json
{
  "imagen_base64": "<imagen en Base64>",
  "modo": "estatica"
}
```

`imagen_base64` es obligatorio y contiene una imagen JPEG o PNG en Base64, sin el prefijo `data:image/...;base64,`. El texto codificado puede contener hasta 7.000.000 de caracteres y la imagen decodificada no puede superar 5 MiB. El valor de `modo` es `estatica` o `movimiento` y, si se omite, el backend utiliza `estatica`.

Para analizar una secuencia con movimiento se puede enviar también `id_secuencia`, que debe tener formato UUID:

```json
{
  "imagen_base64": "<fotograma en Base64>",
  "modo": "movimiento",
  "id_secuencia": "123e4567-e89b-12d3-a456-426614174000"
}
```

El mismo identificador debe acompañar los fotogramas de una misma secuencia. Cuando no se proporciona, el servicio no conserva un historial de fotogramas para ese intento. El historial se mantiene en memoria dentro del proceso del backend, por lo que no constituye almacenamiento permanente en PostgreSQL.

## Respuestas

Cuando reconoce una letra, el backend puede responder:

```json
{
  "letra": "A",
  "mensaje": null
}
```

Si no detecta una mano:

```json
{
  "letra": null,
  "mensaje": "No se detectó una mano"
}
```

Si detecta una mano pero no encuentra una coincidencia:

```json
{
  "letra": null,
  "mensaje": "No se reconoció una letra"
}
```

Estas situaciones se devuelven con HTTP `200`. Un Base64 incorrecto o una imagen no admitida puede generar `400`, mientras que una validación del esquema produce `422`. Cuando ocurre un error interno del reconocimiento, el endpoint devuelve `500`.

## Funcionamiento

Primero se revisa el tamaño y formato del archivo. OpenCV transforma los bytes recibidos en una imagen, después el gestor compartido obtiene la detección de la mano con MediaPipe. Si no encuentra ninguna mano, devuelve el mensaje correspondiente. En caso contrario, selecciona el reconocimiento según `modo`: las letras estáticas se procesan con sus reglas de posición de dedos y las letras con movimiento se analizan utilizando el historial de fotogramas.

El reconocimiento está organizado mediante Strategy y el decorador de medición de tiempo registra la duración de la operación. El resultado de este endpoint **no guarda automáticamente una sesión o un resultado en PostgreSQL**: el registro de la práctica corresponde a las rutas de resultados descritas en [api.md](api.md).

## Prueba y comprobación

Con el backend iniciado, se puede abrir `http://localhost:8000/docs` y buscar `POST /vision/reconocer`. Desde allí se envía un JSON con una imagen real codificada en Base64 y se verifica la respuesta. Los datos escritos arriba son ejemplos y la cadena `<imagen en Base64>` no es una imagen válida.

Las pruebas del procesamiento visual se encuentran en `src/tests/`, incluyendo los casos del servicio de visión y las validaciones de entrada.
