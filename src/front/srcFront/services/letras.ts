import { solicitarApi } from "./api";

export interface Letra {
  id_letra: number;
  letra: string;
  descripcion: string | null;
  ruta_imagen: string | null;
}

// Esto se hace para poder actualizar la descripcion de una letra desde la interfaz del admin
export interface CambiosLetra {
  descripcion?: string;
}

export interface RespuestaActualizacionLetra {
  mensaje: string;
  letra: Letra; 
}

export function obtenerLetras(): Promise<Letra[]> {
  return solicitarApi<Letra[]>("/letras");
}

//Esta funcion lo que nos permite hacer es poder actualizar la info en la DB
export function actualizarLetra(
  idLetra: number, 
  cambios: CambiosLetra,
  token: string,
): Promise<RespuestaActualizacionLetra> {
  return solicitarApi<RespuestaActualizacionLetra>(`/letras/${idLetra}`, {
    method: "PATCH",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(cambios)
  });
}
