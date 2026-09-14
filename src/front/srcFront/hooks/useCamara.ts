import { useEffect, useRef, useState } from "react";

type EstadoCamara = "inactiva" | "solicitando" | "activa" | "error";


// Libera la cámara
function liberarFlujo(flujo: MediaStream | null) {
  flujo?.getTracks().forEach((pista) => pista.stop());
}


// Obtiene un mensaje para el error
function obtenerMensajeError(error: unknown): string {
  const nombre = error instanceof Error ? error.name : "";

  switch (nombre) {
    case "NotAllowedError":
      return "No se permitió el acceso a la cámara. Revisa los permisos del navegador.";

    case "NotFoundError":
      return "No se encontró una cámara conectada.";

    case "NotReadableError":
      return "No se pudo acceder a la cámara. Comprueba si otra aplicación la está utilizando.";

    case "OverconstrainedError":
      return "La cámara no admite la configuración solicitada.";

    default:
      return "No fue posible iniciar la cámara. Intenta nuevamente.";
  }
}


export function useCamara() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const flujoRef = useRef<MediaStream | null>(null);
  const intentoRef = useRef(0);
  const solicitudPendienteRef = useRef(false);

  const [estado, setEstado] = useState<EstadoCamara>("inactiva");
  const [mensajeError, setMensajeError] = useState("");


  // Libera la cámara al salir de la pantalla
  useEffect(() => {
    return () => {
      intentoRef.current += 1;
      solicitudPendienteRef.current = false;

      liberarFlujo(flujoRef.current);
      flujoRef.current = null;
    };
  }, []);


  // Detiene la cámara y cancela el intento actual
  function detenerCamara() {
    intentoRef.current += 1;
    solicitudPendienteRef.current = false;

    liberarFlujo(flujoRef.current);
    flujoRef.current = null;

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setEstado("inactiva");
    setMensajeError("");
  }


  // Solicita permiso e inicia la cámara
  async function iniciarCamara() {
    if (solicitudPendienteRef.current || flujoRef.current) {
      return;
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      setEstado("error");
      setMensajeError(
        "La cámara no está disponible. Abre la aplicación desde localhost o una dirección HTTPS."
      );
      return;
    }

    const video = videoRef.current;

    if (!video) {
      setEstado("error");
      setMensajeError("No se encontró el visor de la cámara.");
      return;
    }

    const intentoActual = ++intentoRef.current;
    let nuevoFlujo: MediaStream | null = null;

    solicitudPendienteRef.current = true;
    setEstado("solicitando");
    setMensajeError("");

    try {
      nuevoFlujo = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: "user",
          width: { ideal: 640 },
          height: { ideal: 480 },
        },
        audio: false,
      });

      // Descarta permisos recibidos después de cancelar o salir
      if (intentoActual !== intentoRef.current) {
        liberarFlujo(nuevoFlujo);
        return;
      }

      flujoRef.current = nuevoFlujo;

      // Informa si se interrumpe la cámara
      nuevoFlujo.getVideoTracks().forEach((pista) => {
        pista.addEventListener(
          "ended",
          () => {
            if (intentoActual !== intentoRef.current) {
              return;
            }

            detenerCamara();
            setEstado("error");
            setMensajeError(
              "La cámara se desconectó o se interrumpió el acceso."
            );
          },
          { once: true }
        );
      });

      video.srcObject = nuevoFlujo;
      await video.play();

      if (intentoActual !== intentoRef.current) {
        liberarFlujo(nuevoFlujo);
        return;
      }

      setEstado("activa");

    } catch (error) {
      liberarFlujo(nuevoFlujo);

      if (intentoActual !== intentoRef.current) {
        return;
      }

      flujoRef.current = null;
      video.srcObject = null;

      setEstado("error");
      setMensajeError(obtenerMensajeError(error));

    } finally {
      if (intentoActual === intentoRef.current) {
        solicitudPendienteRef.current = false;
      }
    }
  }


  return {
    videoRef,
    estado,
    mensajeError,
    iniciarCamara,
    detenerCamara,
  };
}