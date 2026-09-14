// Captura el video y devuelve una imagen JPEG en Base64
export function capturarFotograma(
  video: HTMLVideoElement,
  lienzo: HTMLCanvasElement,
): string | null {
  // Espera a que exista una imagen disponible
  if (
    video.readyState < HTMLMediaElement.HAVE_CURRENT_DATA
    || video.videoWidth === 0
    || video.videoHeight === 0
  ) {
    return null;
  }

  // Limita el tamaño conservando las proporciones
  const escala = Math.min(
    1,
    640 / video.videoWidth,
    480 / video.videoHeight,
  );

  lienzo.width = Math.max(
    1,
    Math.round(video.videoWidth * escala),
  );

  lienzo.height = Math.max(
    1,
    Math.round(video.videoHeight * escala),
  );

  const contexto = lienzo.getContext("2d");

  if (!contexto) {
    throw new Error("No fue posible preparar la captura de cámara.");
  }

  // Copia el fotograma al lienzo
  contexto.drawImage(
    video,
    0,
    0,
    lienzo.width,
    lienzo.height,
  );

  // Convierte el fotograma a JPEG
  const imagen = lienzo.toDataURL("image/jpeg", 0.8);

  // Retira el prefijo para enviar únicamente el Base64
  const contenido = imagen.split(",")[1];

  if (!contenido) {
    throw new Error("No fue posible convertir la captura de cámara.");
  }

  return contenido;
}