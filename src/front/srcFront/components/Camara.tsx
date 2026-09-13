import type { RefObject } from "react";


interface Props {
  videoRef: RefObject<HTMLVideoElement | null>;
  activa: boolean;
  solicitando: boolean;
  mensajeError: string;
}


function Camara({
  videoRef,
  activa,
  solicitando,
  mensajeError,
}: Props) {
  const textoEstado = solicitando
    ? "Solicitando acceso..."
    : activa
      ? "Cámara activa"
      : mensajeError
        ? "Cámara no disponible"
        : "Cámara apagada";

  return (
    <div className="camara">
      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        hidden={!activa}
        aria-label="Vista de la cámara para practicar señas"
        style={{
            
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",  
          objectFit: "contain",  
          transform: "scaleX(-1)",
        }}
      />

      <div className="estadoCamara" role="status">
        {textoEstado}
      </div>

      {!activa && !solicitando && !mensajeError && (
        <p>Activa la cámara para comenzar a practicar.</p>
      )}

      {solicitando && (
        <p>Permite el acceso a la cámara desde el navegador.</p>
      )}

      {mensajeError && (
        <p role="alert">{mensajeError}</p>
      )}
    </div>
  );
}

export default Camara;