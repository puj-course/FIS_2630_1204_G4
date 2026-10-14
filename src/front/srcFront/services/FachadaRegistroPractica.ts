import { ErrorApi } from "./api";
import { obtenerSesion } from "./autenticacion";
import { obtenerIdLetra } from "./letras";
import {
  registrarProgreso,
  type RegistrarProgresoRespuesta,
} from "./progreso";
import {
  registrarResultadoReconocimiento,
  type ResultadoReconocimientoRespuesta,
} from "./resultados";
import {
  crearSesionReconocimiento,
  guardarSesionReconocimiento,
  limpiarSesionReconocimiento,
  obtenerSesionReconocimiento,
} from "./sesiones";

export interface RegistroIntentoPracticaEntrada {
  token: string;
  idLetraObjetivo: number;
  letraDetectada: string;
  confianza: number;
  sigueActivo: () => boolean;
}

export interface SubsistemasRegistroPractica {
  obtenerSesion: typeof obtenerSesion;
  obtenerIdLetra: typeof obtenerIdLetra;
  obtenerSesionReconocimiento: typeof obtenerSesionReconocimiento;
  crearSesionReconocimiento: typeof crearSesionReconocimiento;
  guardarSesionReconocimiento: typeof guardarSesionReconocimiento;
  limpiarSesionReconocimiento: typeof limpiarSesionReconocimiento;
  registrarResultadoReconocimiento:
    typeof registrarResultadoReconocimiento;
  registrarProgreso: typeof registrarProgreso;
}

const subsistemasPorDefecto: SubsistemasRegistroPractica = {
  obtenerSesion,
  obtenerIdLetra,
  obtenerSesionReconocimiento,
  crearSesionReconocimiento,
  guardarSesionReconocimiento,
  limpiarSesionReconocimiento,
  registrarResultadoReconocimiento,
  registrarProgreso,
};

export class FachadaRegistroPractica {
  private readonly subsistemas: SubsistemasRegistroPractica;

  constructor(
    subsistemas: SubsistemasRegistroPractica = subsistemasPorDefecto,
  ) {
    this.subsistemas = subsistemas;
  }

  async registrarIntento(
    datos: RegistroIntentoPracticaEntrada,
  ): Promise<ResultadoReconocimientoRespuesta | null> {
    const {
      token,
      idLetraObjetivo,
      letraDetectada,
      confianza,
      sigueActivo,
    } = datos;

    if (!sigueActivo()) {
      return null;
    }

    if (this.subsistemas.obtenerSesion()?.access_token !== token) {
      throw new Error(
        "La sesión del usuario cambió. Inicia otra práctica.",
      );
    }

    if (
      !Number.isInteger(idLetraObjetivo)
      || idLetraObjetivo <= 0
      || !Number.isFinite(confianza)
      || confianza < 0.8
      || confianza > 1
    ) {
      throw new Error(
        "La detección no contiene datos válidos para registrarla.",
      );
    }

    const idLetraDetectada =
      await this.subsistemas.obtenerIdLetra(letraDetectada);

    if (!sigueActivo()) {
      return null;
    }

    if (
      !Number.isInteger(idLetraDetectada)
      || !idLetraDetectada
      || idLetraDetectada <= 0
    ) {
      throw new Error(
        "No se encontró la letra detectada en el alfabeto.",
      );
    }

    let sesionReconocimiento =
      this.subsistemas.obtenerSesionReconocimiento();

    if (
      !sesionReconocimiento
      || sesionReconocimiento.estado !== "activa"
      || sesionReconocimiento.fecha_fin !== null
    ) {
      if (this.subsistemas.obtenerSesion()?.access_token !== token) {
        throw new Error(
          "La sesión del usuario cambió. Inicia otra práctica.",
        );
      }

      const nuevaSesion =
        await this.subsistemas.crearSesionReconocimiento(token);

      if (
        !sigueActivo()
        || this.subsistemas.obtenerSesion()?.access_token !== token
      ) {
        return null;
      }

      sesionReconocimiento = nuevaSesion.sesion;
      this.subsistemas.guardarSesionReconocimiento(
        sesionReconocimiento,
      );
    }

    if (!sigueActivo()) {
      return null;
    }

    if (this.subsistemas.obtenerSesion()?.access_token !== token) {
      throw new Error(
        "La sesión del usuario cambió. Inicia otra práctica.",
      );
    }

    const idSesion = sesionReconocimiento.id_sesion;

    try {
      return await this.subsistemas.registrarResultadoReconocimiento(
        {
          id_sesion: idSesion,
          id_letra_objetivo: idLetraObjetivo,
          id_letra_detectada: idLetraDetectada,
          confianza,
        },
        token,
      );
    } catch (error) {
      if (
        error instanceof ErrorApi
        && (
          error.codigoEstado === 403
          || error.codigoEstado === 409
        )
      ) {
        this.limpiarSesionInvalida(idSesion);
      }

      throw error;
    }
  }

  registrarProgreso(
    idLetra: number,
    token: string,
  ): Promise<RegistrarProgresoRespuesta> {
    return this.subsistemas.registrarProgreso(
      { id_letra: idLetra },
      token,
    );
  }

  private limpiarSesionInvalida(idSesion: number): void {
    try {
      const almacenada =
        this.subsistemas.obtenerSesionReconocimiento();

      if (almacenada?.id_sesion === idSesion) {
        this.subsistemas.limpiarSesionReconocimiento();
      }
    } catch {
      return;
    }
  }
}