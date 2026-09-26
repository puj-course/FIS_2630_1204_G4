import { useState } from "react";
import { preguntasFrecuentes } from "../utils/preguntasFrecuentes";

interface Props {
  onCerrar: () => void;
}


function Ayuda({ onCerrar }: Props) {
  const [preguntaAbierta, setPreguntaAbierta] = useState<number | null>(null);

  function alternarPregunta(indice: number) {
    setPreguntaAbierta((actual) => (actual === indice ? null : indice));
  }

  return (
    <div className="overlayAyuda" role="presentation" onClick={onCerrar}>
      <div
        className="modalAyuda"
        role="dialog"
        aria-modal="true"
        aria-labelledby="tituloAyuda"
        onClick={(evento) => evento.stopPropagation()}
      >
        <button
          className="botonCerrarAyuda"
          onClick={onCerrar}
          aria-label="Cerrar ayuda"
        >
          ✕
        </button>

        <h2 id="tituloAyuda">Preguntas frecuentes</h2>

        <div className="acordeonAyuda">
          {preguntasFrecuentes.map((item, indice) => {
            const abierta = preguntaAbierta === indice;

            return (
              <div key={indice} className="itemAcordeon">
                <button
                  className="preguntaAcordeon"
                  onClick={() => alternarPregunta(indice)}
                  aria-expanded={abierta}
                >
                  <span>{item.pregunta}</span>
                  <span className="iconoAcordeon">
                    {abierta ? "−" : "+"}
                  </span>
                </button>

                {abierta && (
                  <p className="respuestaAcordeon">{item.respuesta}</p>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default Ayuda;