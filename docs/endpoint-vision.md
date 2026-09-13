# Endpoint de reconocimiento visual

## Objetivo

Permitir que otros componentes envíen una imagen al backend y
obtengan el resultado del reconocimiento de vocales.

Esta implementación corresponde a la issue #151. La captura de
cámara y el envío continuo desde el frontend quedan fuera de su alcance.

## Ruta

POST /vision/reconocer

Content-Type: application/json

## Entrada

La petición debe incluir el campo obligatorio imagen_base64.

```json
{
  "imagen_base64": "<contenido de una imagen codificada en Base64>"
}
```

El valor mostrado es ilustrativo y debe reemplazarse por el contenido
real de una imagen.

Condiciones:

- Se admiten archivos JPEG y PNG.
- Debe enviarse Base64 sin el prefijo data:image/...;base64,.
- El archivo decodificado no puede superar 5 MiB.
- El texto Base64 no puede superar 7.000.000 de caracteres.
- No se admite una cadena vacía.

## Respuestas

### Vocal reconocida — HTTP 200

```json
{
  "letra": "A",
  "mensaje": null
}
```

La letra reconocida puede ser A, E, I, O o U.

### Sin mano detectada — HTTP 200

```json
{
  "letra": null,
  "mensaje": "No se detectó una mano"
}
```

### Mano sin vocal reconocida — HTTP 200

```json
{
  "letra": null,
  "mensaje": "No se reconoció una vocal"
}
```

### Errores

| Código | Situación |
|---|---|
| 400 | Base64 inválido, formato no admitido, archivo superior a 5 MiB o imagen que no puede decodificarse. |
| 422 | La petición incumple el esquema, por ejemplo, falta imagen_base64 o su longitud está fuera de los límites. |
| 500 | Ocurre un fallo interno al cargar el detector o procesar el reconocimiento. |

Los errores 400 y 500 incluyen un campo detail con el mensaje.
Los errores de validación 422 incluyen los detalles de los campos inválidos.

## Funcionamiento

La ruta recibe el JSON y llama a procesar_imagen_base64.
El servicio convierte el Base64 a una imagen BGR de OpenCV.
DetectorMano obtiene los puntos de la mano con MediaPipe.
reconocer_mano utiliza las reglas existentes de reconocer_vocal.

Cada petición se procesa en modo IMAGE, sin requerir un tiempo
enviado por el consumidor. No se utiliza un historial de estabilización
entre peticiones y se procesa la primera mano detectada.

El detector se carga en su primer uso y se reutiliza. Un bloqueo
evita utilizarlo simultáneamente desde varias peticiones.
Los detectores se cierran al apagar el backend.

## Ejecución local

Desde la raíz del proyecto, con el entorno virtual y las dependencias
configurados:

```bash
python -m uvicorn app.main:app --reload
```

La documentación interactiva está disponible en:

http://127.0.0.1:8000/docs

En Swagger, abrir la sección Visión y seleccionar
POST /vision/reconocer.

## Casos de comprobación

| Caso | Resultado esperado |
|---|---|
| Imagen negra sin manos | HTTP 200, letra null y mensaje de mano no detectada. |
| Fotografía de la seña A utilizada en la prueba manual | HTTP 200 y letra A. |
| Texto Base64 inválido | HTTP 400. |
| Petición sin imagen_base64 | HTTP 422. |

El resultado de reconocimiento depende de la imagen y de las reglas
del módulo visual; una imagen válida no garantiza reconocer una vocal.