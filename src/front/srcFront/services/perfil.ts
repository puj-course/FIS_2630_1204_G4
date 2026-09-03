import { solicitarApi } from "./api";
import type { UsuarioAutenticado } from "./autenticacion";


export interface ProgresoPerfil {
  total_letras: number;
  letras_iniciadas: number;
  letras_dominadas: number;
  cantidad_intentos: number;
  cantidad_aciertos: number;
  porcentaje_progreso: number;
}

export interface PerfilUsuario extends UsuarioAutenticado {
  progreso: ProgresoPerfil;
}


export function consultarPerfil(
  token: string
): Promise<PerfilUsuario> {
  return solicitarApi<PerfilUsuario>("/perfil", {
    headers: {
      Authorization: `Bearer ${token}`
    }
  });
}