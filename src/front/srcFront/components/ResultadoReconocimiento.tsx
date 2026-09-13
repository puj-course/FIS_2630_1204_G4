import type { RefObject } from "react";

import { useReconocimiento } from "../hooks/useReconocimiento";


interface Props {
  videoRef: RefObject<HTMLVideoElement | null>;
}


function ResultadoReconocimiento({ videoRef }: Props) {
  const {
    resultado,
    procesando,
    mensajeError,
    reintentar,
  } = useReconocimiento(videoRef);

  return (
    <div className="resultadoReconocimiento">
      <h4>Resultado del reconocimiento</h4>

      {mensajeError ? (
        <>
          <p role="alert">{mensajeError}</p>

          <button
            type="button"
            onClick={reintentar}
          >
            Reintentar reconocimiento
          </button>
        </>
      ) : (
        <>
          <div role="status">
            {resultado?.letra ? (
              <p>
                Vocal detectada: <strong>{resultado.letra}</strong>
              </p>
            ) : (
              <p>
                {resultado?.mensaje
                  ?? "Esperando el primer resultado..."}
              </p>
            )}
          </div>

          <p>
            {procesando
              ? "Analizando imagen..."
              : "Reconocimiento activo"}
          </p>
        </>
      )}
    </div>
  );
}

export default ResultadoReconocimiento;