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

export function cambiarRolUsuario(
  idUsuario: number,
  nuevoRol: "usuario" | "administrador",
  token: string
): Promise<UsuarioListado> {
  return solicitarApi<UsuarioListado>(
    `/usuarios/${idUsuario}/rol`,
    {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ nuevo_rol: nuevoRol })
    }
  );
}

export interface UsuarioDesactivadoRespuesta {
  id_usuario: number;
  nombre: string;
  correo: string;
  rol: string;
  activo: boolean;
}

export function desactivarUsuario(
  idUsuario: number,
  token: string
): Promise<UsuarioDesactivadoRespuesta> {
  return solicitarApi<UsuarioDesactivadoRespuesta>(
    `/usuarios/${idUsuario}/desactivar`,
    {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
}