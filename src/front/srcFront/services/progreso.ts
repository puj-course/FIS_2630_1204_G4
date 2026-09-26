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

export interface RegistrarProgresoEntrada {
  id_letra: number;
}

export interface ProgresoRegistrado {
  id_progreso: number;
  id_usuario: number;
  id_letra: number;
  cantidad_intentos: number;
  cantidad_aciertos: number;
  dominada: boolean;
  fecha_ultima_practica: string | null;
  fecha_actualizacion: string;
}

export interface RegistrarProgresoRespuesta {
  mensaje: string;
  progreso: ProgresoRegistrado;
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

export function registrarProgreso(
  datos: RegistrarProgresoEntrada,
  token: string
): Promise<RegistrarProgresoRespuesta> {
  return solicitarApi<RegistrarProgresoRespuesta>(
    "/progreso",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(datos)
    }
  );
}