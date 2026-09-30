import { solicitarApi } from "./api";


export type ModoReconocimiento =
  | "estatica"
  | "movimiento";


export interface VisionEntrada {
  imagen_base64: string;
  id_secuencia: string;
  modo: ModoReconocimiento;
}


export interface VisionRespuesta {
  letra:
    | "A"
    | "B"
    | "C"
    | "D"
    | "E"
    | "F"
    | "G"
    | "H"
    | "I"
    | "J"
    | "K"
    | "L"
    | "M"
    | "N"
    | "Ñ"
    | "O"
    | "P"
    | "Q"
    | "R"
    | "S"
    | "T"
    | "U"
    | "V"
    | "W"
    | "X"
    | "Y"
    | "Z"
    | null;
  mensaje: string | null;
}



export function reconocerImagen(
  imagenBase64: string,
  idSecuencia: string,
  modo: ModoReconocimiento,
  signal?: AbortSignal,
): Promise<VisionRespuesta> {
  const datos: VisionEntrada = {
    imagen_base64: imagenBase64,
    id_secuencia: idSecuencia,
    modo,
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