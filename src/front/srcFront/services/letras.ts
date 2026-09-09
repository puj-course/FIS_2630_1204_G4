import { solicitarApi } from "./api";

export interface Letra {
  id_letra: number;
  letra: string;
  descripcion: string | null;
  ruta_imagen: string | null;
}

export interface LetraActualizacion {
  descripcion?: string;
  ruta_imagen?: string;
}

export interface LetraActualizacionRespuesta {
  mensaje: string;
  letra: Letra;
}

export function obtenerLetras(): Promise<Letra[]> {
  return solicitarApi<Letra[]>("/letras");
}

export function actualizarLetra(
  idLetra: number,
  datos: LetraActualizacion,
  token: string
): Promise<LetraActualizacionRespuesta> {
  return solicitarApi<LetraActualizacionRespuesta>(
    `/letras/${idLetra}`,
    {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(datos)
    }
  );
}