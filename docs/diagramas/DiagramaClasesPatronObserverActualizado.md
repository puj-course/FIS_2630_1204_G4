# Diagrama de clases — Patrón Observer: EventosPractica

## Propósito

Este diagrama muestra la estructura del patrón **Observer** en el frontend de SignIA. El patrón se usa en la pantalla de práctica para avisar a las partes interesadas cuando se registra un intento de reconocimiento o se actualiza el progreso de una letra, sin que el componente que origina el evento tenga que conocerlas.

## Diagrama

<img width="790" height="482" alt="c40b23e0-9222-49ca-8b5f-8de4bee2bf04" src="https://github.com/user-attachments/assets/548e4e48-a245-4cb7-beb1-a170f62b98ac" />


## Archivos de origen

| Archivo | Qué aporta al diagrama |
|---|---|
| `src/front/srcFront/events/EventosPractica.ts` | Define el tipo `EventoPractica`, las interfaces `SujetoPractica` y `ObservadorPractica`, y la clase `EventosPractica`. |
| `src/front/srcFront/Practica.tsx` | Crea la instancia de `EventosPractica` y define y suscribe los observadores concretos. |
| `src/front/srcFront/components/ResultadoReconocimiento.tsx` | Emite los eventos llamando a `notificar`. |

## Elementos del diagrama

| Elemento | Tipo en el código | Rol en Observer | Descripción |
|---|---|---|---|
| `SujetoPractica` | `interface` | Sujeto | Declara `suscribir`, `desuscribir` y `notificar`. |
| `ObservadorPractica` | `interface` | Observador | Declara `actualizar(evento)`, que cada observador implementa. |
| `EventosPractica` | `class` | Sujeto concreto | Implementa `SujetoPractica`. Guarda los observadores en un `Set` privado y, al notificar, llama a `actualizar(evento)` en cada uno. |
| `EventoPractica` | Tipo unión de TypeScript (`<<type>>`) | Mensaje notificado | Puede ser `{ tipo: "intentoRegistrado" }` o `{ tipo: "progresoRegistrado"; idLetra: number }`. |

## Relaciones

| Relación | Notación | Significado |
|---|---|---|
| `EventosPractica` → `SujetoPractica` | Realización (línea punteada con triángulo hueco) | `EventosPractica` implementa la interfaz `SujetoPractica`. |
| `EventosPractica` → `ObservadorPractica` | Asociación dirigida, `-observadores 0..* {unique}` | El sujeto concreto mantiene una colección privada de cero o más observadores, sin repetidos (un `Set`). Los observadores no tienen referencia al sujeto. |
| `SujetoPractica` → `EventoPractica` | Dependencia `«use»` | `notificar` recibe un `EventoPractica`. |
| `ObservadorPractica` → `EventoPractica` | Dependencia `«use»` | `actualizar` recibe un `EventoPractica`. |

## Funcionamiento

1. `Practica.tsx` crea una instancia de `EventosPractica`.
2. `Practica.tsx` define dos observadores y los suscribe con `suscribir`. Al desmontarse, los desuscribe con `desuscribir`.
3. `Practica.tsx` pasa el sujeto a `ResultadoReconocimiento`, que lo recibe con el tipo de la interfaz `SujetoPractica`.
4. Cuando `ResultadoReconocimiento` registra un intento, llama a `notificar({ tipo: "intentoRegistrado" })`. Si el intento es correcto y se registra el progreso, llama a `notificar({ tipo: "progresoRegistrado", idLetra })`.
5. `EventosPractica` recorre todos los observadores suscritos y ejecuta `actualizar(evento)` en cada uno. Si un observador falla, registra el error y continúa con los demás.
6. Cada observador revisa el `tipo` del evento y reacciona solo al que le corresponde.

## Observadores concretos

Los observadores concretos son **objetos literales** que implementan `ObservadorPractica` dentro de `Practica.tsx`. **No son clases**, por eso no aparecen como cajas en el diagrama; se mencionan en una nota.

| Observador | Evento que atiende | Reacción |
|---|---|---|
| `observadorHistorial` | `intentoRegistrado` | Vuelve a cargar el historial de intentos. |
| `observadorConfirmacion` | `progresoRegistrado` | Si la modalidad confirma la letra objetivo, detiene la cámara y muestra la confirmación de aprendizaje. |

## Alcance y omisiones

- El diagrama representa solo la **estructura del patrón Observer**.
- `Practica` y `ResultadoReconocimiento` son **componentes funcionales de React**, no clases, por eso no se dibujan como cajas.
- Se omiten otros elementos de esos archivos que no forman parte del patrón (servicios, hooks, modalidades y la fachada de registro). Siguen existiendo en el código, aunque no aparezcan en el diagrama.
- El atributo privado `observadores` no se muestra dentro de la caja de `EventosPractica` porque ya está representado por la asociación.
