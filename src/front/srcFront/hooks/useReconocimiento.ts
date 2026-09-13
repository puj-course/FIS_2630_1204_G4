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


export function useReconocimiento(
  videoRef: RefObject<HTMLVideoElement | null>,
) {
  const [resultado, setResultado] =
    useState<VisionRespuesta | null>(null);

  const [procesando, setProcesando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");
  const [intento, setIntento] = useState(0);


  useEffect(() => {
    let activo = true;
    let temporizador: number | undefined;
    let limiteEspera: number | undefined;
    let peticion: AbortController | null = null;


    async function procesarFotograma() {
      if (!activo) {
        return;
      }

      let tiempoAgotado = false;

      try {
        const video = videoRef.current;

        // Espera a que el visor esté disponible
        if (!video) {
          temporizador = window.setTimeout(
            procesarFotograma,
            200,
          );
          return;
        }

        const imagenBase64 = capturarFotograma(video, lienzo);

        // Espera a que exista un fotograma
        if (!imagenBase64) {
          temporizador = window.setTimeout(
            procesarFotograma,
            200,
          );
          return;
        }

        const controlador = new AbortController();
        peticion = controlador;

        // Limita el tiempo de espera de la petición
        limiteEspera = window.setTimeout(() => {
          tiempoAgotado = true;
          controlador.abort();
        }, 15000);

        setProcesando(true);

        // Envía una imagen y espera la respuesta
        const respuesta = await reconocerImagen(
          imagenBase64,
          controlador.signal,
        );

        if (!activo) {
          return;
        }

        setResultado(respuesta);
        setMensajeError("");

        // Programa la siguiente captura después de recibir respuesta
        temporizador = window.setTimeout(
          procesarFotograma,
          400,
        );

      } catch (error) {
        if (!activo) {
          return;
        }

        setResultado(null);

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


    // Crea un lienzo reutilizable para las capturas
    const lienzo = document.createElement("canvas");

    temporizador = window.setTimeout(
      procesarFotograma,
      0,
    );


    // Detiene el envío y descarta las respuestas pendientes
    return () => {
      activo = false;

      window.clearTimeout(temporizador);
      window.clearTimeout(limiteEspera);

      peticion?.abort();
    };
  }, [videoRef, intento]);


  // Inicia otro intento después de un error
  function reintentar() {
    setResultado(null);
    setMensajeError("");
    setProcesando(false);
    setIntento((anterior) => anterior + 1);
  }


  return {
    resultado,
    procesando,
    mensajeError,
    reintentar,
  };
}
