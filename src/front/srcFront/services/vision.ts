import { solicitarApi } from "./api";


export interface VisionEntrada {
  imagen_base64: string;
  id_secuencia?: string;
}


export interface VisionRespuesta {
  letra:
    | "A"
    | "E"
    | "G"
    | "H"
    | "I"
    | "J"
    | "Ñ"
    | "O"
    | "S"
    | "U"
    | "Z"
    | null;
  mensaje: string | null;
}


// Envía un fotograma al servicio de reconocimiento
export function reconocerImagen(
  imagenBase64: string,
  idSecuencia: string,
  signal?: AbortSignal,
): Promise<VisionRespuesta> {
  const datos: VisionEntrada = {
    imagen_base64: imagenBase64,
    id_secuencia: idSecuencia,
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