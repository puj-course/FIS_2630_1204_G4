import {
  useEffect,
  useState,
  type RefObject,
} from "react";

import {
  reconocerImagen,
  type VisionRespuesta,
} from "../services/vision";

import { capturarFotograma } from "../utils/capturarFotograma";


const TAMANO_HISTORIAL = 5;


export function useReconocimiento(
  videoRef: RefObject<HTMLVideoElement | null>,
) {
  const [resultado, setResultado] =
    useState<VisionRespuesta | null>(null);

  const [confianza, setConfianza] =
    useState<number | null>(null);

  const [procesando, setProcesando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");
  const [intento, setIntento] = useState(0);


  useEffect(() => {
    let activo = true;
    let temporizador: number | undefined;
    let limiteEspera: number | undefined;
    let peticion: AbortController | null = null;

    const historial: Array<VisionRespuesta["letra"]> = [];


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
          controlador.signal,
        );

        if (!activo) {
          return;
        }

        historial.push(respuesta.letra);

        if (historial.length > TAMANO_HISTORIAL) {
          historial.shift();
        }

        const coincidencias = respuesta.letra
          ? historial.filter(
              (letra) => letra === respuesta.letra
            ).length
          : 0;

        const confianzaCalculada = (
          respuesta.letra
          && historial.length === TAMANO_HISTORIAL
        )
          ? coincidencias / TAMANO_HISTORIAL
          : null;

        setResultado(respuesta);
        setConfianza(confianzaCalculada);
        setMensajeError("");

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


    const lienzo = document.createElement("canvas");

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
  }, [videoRef, intento]);


  function reintentar() {
    setResultado(null);
    setConfianza(null);
    setMensajeError("");
    setProcesando(false);
    setIntento((anterior) => anterior + 1);
  }


  return {
    resultado,
    confianza,
    procesando,
    mensajeError,
    reintentar,
  };
}