import type { VisionRespuesta } from "../services/vision";

type LetraDetectada = VisionRespuesta["letra"];

const TAMANO_HISTORIAL = 5;
const ESTABILIDAD_MINIMA = 0.8;
const FOTOGRAMAS_PARA_REINICIAR = 3;

export interface EvaluacionIntento {
  confianza: number | null;
  nuevoIntento: boolean;
}

export function crearControlIntentos() {
  const historial: LetraDetectada[] = [];

  let ultimaLetraRegistrada: LetraDetectada = null;
  let fotogramasSinLetra = 0;

  function evaluar(
    letra: LetraDetectada,
  ): EvaluacionIntento {
    historial.push(letra);

    if (historial.length > TAMANO_HISTORIAL) {
      historial.shift();
    }

    if (letra === null) {
      fotogramasSinLetra += 1;

      if (
        fotogramasSinLetra
        >= FOTOGRAMAS_PARA_REINICIAR
      ) {
        ultimaLetraRegistrada = null;
        historial.length = 0;
      }

      return {
        confianza: null,
        nuevoIntento: false,
      };
    }

    fotogramasSinLetra = 0;

    if (historial.length < TAMANO_HISTORIAL) {
      return {
        confianza: null,
        nuevoIntento: false,
      };
    }

    const coincidencias = historial.filter(
      (anterior) => anterior === letra,
    ).length;

    const confianza =
      coincidencias / TAMANO_HISTORIAL;

    const nuevoIntento =
      confianza >= ESTABILIDAD_MINIMA
      && letra !== ultimaLetraRegistrada;

    if (nuevoIntento) {
      ultimaLetraRegistrada = letra;
    }

    return {
      confianza,
      nuevoIntento,
    };
  }

  return {
    evaluar,
  };
}