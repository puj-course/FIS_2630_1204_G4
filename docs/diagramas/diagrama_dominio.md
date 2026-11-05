# Diagrama de clases de dominio — SignIA

<img width="1038" height="756" alt="Diagrama de dominio" src="https://github.com/user-attachments/assets/10629d48-ff00-4a9e-b48f-255d5b81cf4f" />


## Descripción

Este diagrama representa el **modelo de dominio** de SignIA: los conceptos que el sistema guarda, sus atributos y cómo se relacionan entre sí.

El proyecto no tiene clases de entidad (la carpeta `src/models` está vacía), así que el modelo se construyó a partir de:

- `database/schema.sql`
- `database/migrations/intentos_reconocimiento.sql`
- `database/migrations/agregar_resultado_a_intentos.sql`
- `database/migrations/recuperaciones_contrasena.sql`
- `app/services/resultados_service.py`, para confirmar que `id_letra` del intento es la **letra objetivo**

Es un diagrama de clases UML de nivel conceptual. Por eso:

- No muestra visibilidad ni operaciones.
- Las asociaciones no indican navegabilidad.

## Enumeraciones

| Enumeración | Valores | Origen |
|---|---|---|
| `Rol` | `usuario`, `administrador` | `CHECK` de `usuarios.rol` |
| `EstadoSesion` | `activa`, `finalizada`, `cancelada` | `CHECK` de `sesiones_reconocimiento.estado` |

Las enumeraciones no tienen líneas de asociación porque se usan como **tipo de atributo**:

- `Usuario.rol : Rol`
- `SesionReconocimiento.estado : EstadoSesion`

## Clases

| Clase | Tabla | Qué representa |
|---|---|---|
| `Usuario` | `usuarios` | Persona registrada que practica o administra el sistema. |
| `Letra` | `letras` | Letra del alfabeto de señas que se puede practicar. |
| `SesionReconocimiento` | `sesiones_reconocimiento` | Sesión de práctica iniciada por un usuario. |
| `ResultadoReconocimiento` | `resultados_reconocimiento` | Resultado de comparar la letra objetivo con la letra detectada por la cámara. |
| `IntentoReconocimiento` | `intentos_reconocimiento` | Intento registrado a partir de un resultado, para el historial del usuario. |
| `ProgresoUsuario` | `progreso_usuario` | Avance acumulado de un usuario en una letra. |
| `RecuperacionContrasena` | `recuperaciones_contrasena` | Solicitud de recuperación de cuenta. |

El atributo `/esCorrecto` de `ResultadoReconocimiento` es **derivado**: la base de datos obliga a que sea igual a comparar `letraObjetivo` con `letraDetectada`.

## Asociaciones

| Asociación | Multiplicidad | Nombre / rol | Evidencia |
|---|---|---|---|
| `Usuario` — `RecuperacionContrasena` | `1` — `0..*` | `solicita` | FK `id_usuario` |
| `Usuario` — `SesionReconocimiento` | `1` — `0..*` | `inicia` | FK `id_usuario` |
| `Usuario` — `ProgresoUsuario` | `1` — `0..*` | — | FK `id_usuario` |
| `Usuario` — `Letra` | `0..1` — `0..*` | `crea`, rol `creadaPor` | FK `creada_por`, admite nulos |
| `Usuario` — `IntentoReconocimiento` | `1` — `0..*` | `realiza` | FK `id_usuario` |
| `SesionReconocimiento` — `ResultadoReconocimiento` | `1` — `0..*` | `genera` | FK `id_sesion` |
| `SesionReconocimiento` — `IntentoReconocimiento` | `1` — `0..*` | — | FK `id_sesion` |
| `ResultadoReconocimiento` — `IntentoReconocimiento` | `1` — `0..1` | `origina` | FK `id_resultado` + `UNIQUE (id_resultado)` |
| `ResultadoReconocimiento` — `Letra` | `0..*` — `1` | rol `letraObjetivo` | FK `id_letra_objetivo` |
| `ResultadoReconocimiento` — `Letra` | `0..*` — `1` | rol `letraDetectada` | FK `id_letra_detectada` |
| `IntentoReconocimiento` — `Letra` | `0..*` — `1` | rol `letraObjetivo` | FK `id_letra` (`resultados_service.py` le pasa `id_letra_objetivo`) |
| `ProgresoUsuario` — `Letra` | `0..*` — `1` | — | FK `id_letra` |

`ResultadoReconocimiento` tiene **dos** asociaciones con `Letra`:

- una con la letra que el usuario debía hacer (`letraObjetivo`);
- otra con la letra que detectó el reconocimiento (`letraDetectada`).

## Restricciones (notas del diagrama)

- **`ProgresoUsuario`**:
  - `{único por (usuario, letra)}`, por el `UNIQUE (id_usuario, id_letra)`.
  - `{cantidadAciertos <= cantidadIntentos}`.
- **`ResultadoReconocimiento`**:
  - `{0 <= confianza <= 1}`.
  - `{esCorrecto = (letraObjetivo = letraDetectada)}`.
- **`IntentoReconocimiento`**: referencia al usuario de dos formas: directamente y a través de la sesión. El esquema no obliga a que ambos sean el mismo usuario.

## Elementos omitidos

| Omitido | Motivo |
|---|---|
| Identificadores (`id_*`) y claves foráneas | En un modelo de dominio se representan con asociaciones, no con atributos. |
| `contrasena_hash`, `intentos_fallidos`, `bloqueado_hasta`, `token_hash` | Son detalles de seguridad de la implementación, no conceptos del dominio. |
| Tabla `tokens_revocados` | Es un mecanismo técnico de la autenticación JWT, no un concepto del dominio. |
| Operaciones y visibilidad | El diagrama es conceptual: solo modela datos y relaciones. |
