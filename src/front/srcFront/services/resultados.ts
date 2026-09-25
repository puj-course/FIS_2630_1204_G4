import { solicitarApi } from "./api";

export interface ResultadoReconocimientoEntrada {
  id_letra_objetivo: number;
  letra_detectada: string;
  confianza: number;
}

export interface ResultadoRegistrado {
  id_resultado: number;
  id_sesion: number;
  id_usuario: number;
  id_letra_objetivo: number;
  letra_objetivo: string;
  id_letra_detectada: number;
  letra_detectada: string;
  confianza: number;
  es_correcto: boolean;
  fecha_resultado: string;
}

export interface ResultadoReconocimientoRespuesta {
  mensaje: string;
  resultado: ResultadoRegistrado;
}

export interface ResultadosReconocimientoConsultaRespuesta {
  total: number;
  resultados: ResultadoRegistrado[];
}

export function registrarResultadoReconocimiento(
  datos: ResultadoReconocimientoEntrada,
  token: string
): Promise<ResultadoReconocimientoRespuesta> {
  return solicitarApi<ResultadoReconocimientoRespuesta>(
    "/resultados-reconocimiento",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify(datos)
    }
  );
}

export function consultarResultadosReconocimiento(
  token: string
): Promise<ResultadosReconocimientoConsultaRespuesta> {
  return solicitarApi<ResultadosReconocimientoConsultaRespuesta>(
    "/resultados-reconocimiento",
    {
      headers: {
        Authorization: `Bearer ${token}`
      }
    }
  );
}