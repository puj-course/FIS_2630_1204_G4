import { useState } from "react";

interface PreguntaFrecuente {
  pregunta: string;
  respuesta: string;
}

interface Props {
  onCerrar: () => void;
}

const preguntasFrecuentes: PreguntaFrecuente[] = [
  {
    pregunta: "¿Cómo activo la cámara para practicar?",
    respuesta:
      "En la sección \"Practicar\", haz clic en el botón \"Activar cámara\" y acepta el permiso que te pida el navegador."
  },
  {
    pregunta: "¿Por qué no reconoce mi seña correctamente?",
    respuesta:
      "Asegúrate de tener buena iluminación y de que tu mano esté completa dentro del encuadre de la cámara."
  },
  {
    pregunta: "¿Cómo se calcula mi progreso?",
    respuesta:
      "Tu progreso se calcula según las letras que has practicado y dominado del alfabeto LSC."
  },
  {
    pregunta: "¿Puedo cambiar mi meta diaria de práctica?",
    respuesta:
      "Sí, desde tu perfil puedes seleccionar cuántas señas quieres practicar cada día."
  },
  {
    pregunta: "¿Qué hago si olvidé mi contraseña?",
    respuesta:
      "En la pantalla de inicio de sesión, usa la opción \"¿Olvidaste tu contraseña?\" para recuperarla por correo."
  }
];

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