import { solicitarApi } from "./api";


export interface SolicitudRecuperacion {
  correo: string;
}


export interface RespuestaRecuperacion {
  mensaje: string;
}


export function solicitarRecuperacion(
  datos: SolicitudRecuperacion
): Promise<RespuestaRecuperacion> {

  return solicitarApi<RespuestaRecuperacion>(
    "/auth/recuperar-contrasena",
    {
      method: "POST",
      body: JSON.stringify(datos)
    }
  );
}


export interface SolicitudRestablecimiento {
  token: string;
  nueva_contrasena: string;
  confirmacion_contrasena: string;
}


export interface RespuestaRestablecimiento {
  mensaje: string;
}


export function restablecerContrasena(
  datos: SolicitudRestablecimiento
): Promise<RespuestaRestablecimiento> {
  return solicitarApi<RespuestaRestablecimiento>(
    "/auth/restablecer-contrasena",
    {
      method: "POST",
      body: JSON.stringify(datos)
    }
  );
}