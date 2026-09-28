import { solicitarApi } from "./api";

export interface UsuarioListado {
  id_usuario: number;
  nombre: string;
  correo: string;
  rol: "usuario" | "administrador";
  fecha_creacion: string;
}

export function obtenerUsuarios(
  buscar: string,
  token: string
): Promise<UsuarioListado[]> {
  const parametros = buscar.trim()
    ? `?buscar=${encodeURIComponent(buscar.trim())}`
    : "";

  return solicitarApi<UsuarioListado[]>(
    `/usuarios${parametros}`,
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
}