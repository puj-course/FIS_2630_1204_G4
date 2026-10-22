import type { Letra } from "../services/letras";

export type TipoModalidad = "libre" | "especifica";

export interface ModalidadPractica {
  readonly tipo: TipoModalidad;
  readonly descripcion: string;
  readonly muestraHistorial: boolean;
  titulo(nombreLetra: string | null): string;
  idLetraObjetivo(letra: Letra | null): number | null;
  confirmaReconocimiento(idLetra: number, letra: Letra): boolean;
}

class PracticaLibre implements ModalidadPractica {
  readonly tipo: TipoModalidad = "libre";
  readonly muestraHistorial = false;
  readonly descripcion =
    "Practica libremente el alfabeto de la Lengua de Señas Colombiana con visión por computadora.";

  titulo(): string {
    return "Práctica Libre";
  }

  idLetraObjetivo(): number | null {
    return null;
  }

  confirmaReconocimiento(): boolean {
    return false;
  }
}

class PracticaEspecifica implements ModalidadPractica {
  readonly tipo: TipoModalidad = "especifica";
  readonly muestraHistorial = true;
  readonly descripcion =
    "Practica una letra específica de la Lengua de Señas Colombiana con visión por computadora.";

  titulo(nombreLetra: string | null): string {
    return nombreLetra
      ? `Práctica Específica: ${nombreLetra}`
      : "Práctica Libre";
  }

  idLetraObjetivo(letra: Letra | null): number | null {
    return letra?.id_letra ?? null;
  }

  confirmaReconocimiento(idLetra: number, letra: Letra): boolean {
    return letra.id_letra === idLetra;
  }
}

export abstract class CreadorModalidad {
  protected abstract crearModalidad(): ModalidadPractica;

  obtenerModalidad(): ModalidadPractica {
    return this.crearModalidad();
  }
}

export class CreadorPracticaLibre extends CreadorModalidad {
  protected crearModalidad(): ModalidadPractica {
    return new PracticaLibre();
  }
}

export class CreadorPracticaEspecifica extends CreadorModalidad {
  protected crearModalidad(): ModalidadPractica {
    return new PracticaEspecifica();
  }
}

const creadores: Record<TipoModalidad, CreadorModalidad> = {
  libre: new CreadorPracticaLibre(),
  especifica: new CreadorPracticaEspecifica(),
};

export function crearModalidad(tipo: TipoModalidad): ModalidadPractica {
  return creadores[tipo].obtenerModalidad();
}