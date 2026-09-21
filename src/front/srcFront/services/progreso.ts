import { solicitarApi } from "./api";

export type EstadoAprendizaje = "aprendida" | "pendiente";

export interface EstadoLetra {
  id_letra: number;
  letra: string;
  descripcion: string | null;
  ruta_imagen: string | null;
  estado: EstadoAprendizaje;
}

export interface ConsultaEstadoLetrasRespuesta {
  total: number;
  letras: EstadoLetra[];
}

export function consultarEstadoLetras(
  token: string
): Promise<ConsultaEstadoLetrasRespuesta> {
  return solicitarApi<ConsultaEstadoLetrasRespuesta>(
    "/progreso/letras",
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
}