import { solicitarApi } from "./api";

export interface SesionReconocimiento {
  id_sesion: number;
  id_usuario: number;
  fecha_inicio: string;
  fecha_fin: string | null;
  estado: string;
}

export interface CrearSesionRespuesta {
  mensaje: string;
  sesion: SesionReconocimiento;
}


export function crearSesionReconocimiento(
  token: string
): Promise<CrearSesionRespuesta> {
  return solicitarApi<CrearSesionRespuesta>(
    "/sesiones",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );
}

const CLAVE_SESION =
  "sesion_reconocimiento";


export function guardarSesionReconocimiento(
  sesion: SesionReconocimiento
) {
  localStorage.setItem(
    CLAVE_SESION,
    JSON.stringify(sesion)
  );
}


export function obtenerSesionReconocimiento():
  SesionReconocimiento | null {

  const datos =
    localStorage.getItem(CLAVE_SESION);

  if (!datos) {
    return null;
  }

  return JSON.parse(datos);
}

export function limpiarSesionReconocimiento() {
  localStorage.removeItem(CLAVE_SESION);
}