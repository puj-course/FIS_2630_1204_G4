import {
  useEffect,
  useState,
  type RefObject,
} from "react";

import {
  reconocerImagen,
  type ModoReconocimiento,
  type VisionRespuesta,
} from "../services/vision";

import { capturarFotograma } from "../utils/capturarFotograma";
import { crearControlIntentos } from "../utils/controlIntentos";

export interface IntentoReconocido {
  id: string;
  letra: NonNullable<VisionRespuesta["letra"]>;
  confianza: number;
  modo: ModoReconocimiento;
}

export function useReconocimiento(
  videoRef: RefObject<HTMLVideoElement | null>,
  modo: ModoReconocimiento,
) {
  const [resultado, setResultado] =
    useState<VisionRespuesta | null>(null);

  const [confianza, setConfianza] =
    useState<number | null>(null);

  const [intentoReconocido, setIntentoReconocido] =
    useState<IntentoReconocido | null>(null);

  const [procesando, setProcesando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let activo = true;
    let temporizador: number | undefined;
    let limiteEspera: number | undefined;
    let peticion: AbortController | null = null;

    const idSecuencia = crypto.randomUUID();
    const lienzo = document.createElement("canvas");
    const controlIntentos = crearControlIntentos();

    async function procesarFotograma() {
      if (!activo) {
        return;
      }

      let tiempoAgotado = false;

      try {
        const video = videoRef.current;

        if (!video) {
          temporizador = window.setTimeout(
            procesarFotograma,
            200,
          );
          return;
        }

        const imagenBase64 = capturarFotograma(
          video,
          lienzo,
        );

        if (!imagenBase64) {
          temporizador = window.setTimeout(
            procesarFotograma,
            200,
          );
          return;
        }

        const controlador = new AbortController();
        peticion = controlador;

        limiteEspera = window.setTimeout(() => {
          tiempoAgotado = true;
          controlador.abort();
        }, 15000);

        setProcesando(true);

        const respuesta = await reconocerImagen(
          imagenBase64,
          idSecuencia,
          modo,
          controlador.signal,
        );

        if (!activo) {
          return;
        }

        const evaluacion = controlIntentos.evaluar(
          respuesta.letra,
        );

        setResultado(respuesta);
        setConfianza(evaluacion.confianza);
        setMensajeError("");

        if (
          evaluacion.nuevoIntento
          && respuesta.letra !== null
          && evaluacion.confianza !== null
        ) {
          setIntentoReconocido({
            id: crypto.randomUUID(),
            letra: respuesta.letra,
            confianza: evaluacion.confianza,
            modo,
          });
        }

        temporizador = window.setTimeout(
          procesarFotograma,
          400,
        );
      } catch (error) {
        if (!activo) {
          return;
        }

        setResultado(null);
        setConfianza(null);
        setIntentoReconocido(null);

        setMensajeError(
          tiempoAgotado
            ? "El reconocimiento tardó demasiado. Intenta nuevamente."
            : error instanceof Error
              ? error.message
              : "No fue posible obtener el reconocimiento.",
        );
      } finally {
        window.clearTimeout(limiteEspera);
        peticion = null;

        if (activo) {
          setProcesando(false);
        }
      }
    }

    temporizador = window.setTimeout(
      procesarFotograma,
      0,
    );

    return () => {
      activo = false;

      window.clearTimeout(temporizador);
      window.clearTimeout(limiteEspera);

      peticion?.abort();
    };
  }, [videoRef, intento, modo]);

  function reintentar() {
    setResultado(null);
    setConfianza(null);
    setIntentoReconocido(null);
    setMensajeError("");
    setProcesando(false);
    setIntento((anterior) => anterior + 1);
  }

  return {
    resultado,
    confianza,
    intentoReconocido,
    procesando,
    mensajeError,
    reintentar,
  };
}