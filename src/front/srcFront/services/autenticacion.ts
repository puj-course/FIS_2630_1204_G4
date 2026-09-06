import { solicitarApi } from "./api";


export interface UsuarioAutenticado {
  id_usuario: number;
  nombre: string;
  correo: string;
  rol: "usuario" | "administrador";
}

export interface RespuestaLogin {
  access_token: string;
  token_type: string;
  usuario: UsuarioAutenticado;
}

export interface DatosRegistro {
  nombre: string;
  correo: string;
  contrasena: string;
}

export interface RespuestaRegistro {
  mensaje: string;
  usuario: UsuarioAutenticado;
}

interface CredencialesLogin {
  correo: string;
  contrasena: string;
}

const CLAVE_SESION = "signia_sesion";


export function iniciarSesion(
  credenciales: CredencialesLogin
): Promise<RespuestaLogin> {
  return solicitarApi<RespuestaLogin>("/auth/login", {
    method: "POST",
    body: JSON.stringify(credenciales)
  });
}

export function registrarUsuario(
  datos: DatosRegistro
): Promise<RespuestaRegistro> {
  return solicitarApi<RespuestaRegistro>("/auth/registro", {
    method: "POST",
    body: JSON.stringify(datos)
  });
}

export function guardarSesion(sesion: RespuestaLogin): void {
  sessionStorage.setItem(
    CLAVE_SESION,
    JSON.stringify(sesion)
  );
}

export function obtenerSesion(): RespuestaLogin | null {
  const sesionGuardada = sessionStorage.getItem(CLAVE_SESION);

  if (!sesionGuardada) {
    return null;
  }

  try {
    return JSON.parse(sesionGuardada) as RespuestaLogin;
  } catch {
    sessionStorage.removeItem(CLAVE_SESION);
    return null;
  }
}

export function eliminarSesion(): void {
  sessionStorage.removeItem(CLAVE_SESION);
}