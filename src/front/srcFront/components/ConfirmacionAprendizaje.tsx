import { useEffect, useRef } from "react";
import { FaCheckCircle } from "react-icons/fa";
import "./ConfirmacionAprendizaje.css";

interface Props {
  letra: string;
  onVolverAprender: () => void;
  onVerPerfil: () => void;
}

function ConfirmacionAprendizaje({
  letra,
  onVolverAprender,
  onVerPerfil,
}: Props) {
  const dialogoRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialogo = dialogoRef.current;

    if (dialogo && !dialogo.open) {
      dialogo.showModal();
    }

    return () => {
      if (dialogo?.open) {
        dialogo.close();
      }
    };
  }, []);

  return (
    <dialog
      ref={dialogoRef}
      className="confirmacionAprendizaje"
      aria-modal="true"
      aria-labelledby="tituloConfirmacionAprendizaje"
      aria-describedby="descripcionConfirmacionAprendizaje"
      onCancel={(evento) => evento.preventDefault()}
    >
      <FaCheckCircle
        className="confirmacionAprendizajeIcono"
        aria-hidden="true"
      />

      <h2 id="tituloConfirmacionAprendizaje">
        ¡Aprendiste la letra{" "}
        <span className="confirmacionAprendizajeLetra">
          {letra}
        </span>
        !
      </h2>

      <p id="descripcionConfirmacionAprendizaje">
        Tu seña fue reconocida correctamente y tu progreso se actualizó.
      </p>

      <div className="confirmacionAprendizajeAcciones">
        <button type="button" onClick={onVolverAprender}>
          Volver a Aprender
        </button>
        <button type="button" onClick={onVerPerfil}>
          Ver mi perfil
        </button>
      </div>
    </dialog>
  );
}

export default ConfirmacionAprendizaje;