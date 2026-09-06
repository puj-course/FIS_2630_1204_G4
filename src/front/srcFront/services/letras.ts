import { solicitarApi } from "./api";

export interface Letra {
  id_letra: number;
  letra: string;
  descripcion: string | null;
  ruta_imagen: string | null;
}

export function obtenerLetras(): Promise<Letra[]> {
  return solicitarApi<Letra[]>("/letras");
}