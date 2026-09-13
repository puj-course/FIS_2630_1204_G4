import { solicitarApi } from "./api";


export interface VisionEntrada {
  imagen_base64: string;
}


export interface VisionRespuesta {
  letra: "A" | "E" | "I" | "O" | "U" | null;
  mensaje: string | null;
}


// Envía una imagen al servicio de reconocimiento
export function reconocerImagen(
  imagenBase64: string,
  signal?: AbortSignal,
): Promise<VisionRespuesta> {
  const datos: VisionEntrada = {
    imagen_base64: imagenBase64,
  };

  return solicitarApi<VisionRespuesta>(
    "/vision/reconocer",
    {
      method: "POST",
      body: JSON.stringify(datos),
      signal,
    },
  );
}