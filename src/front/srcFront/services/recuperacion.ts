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