import { useState } from "react";

interface Paso {
  titulo: string;
  descripcion: string;
}

interface Props {
  onCerrar: () => void;
}

const pasos: Paso[] = [
  {
    titulo: "¡Bienvenido a SignIA!",
    descripcion:
      "Aprende y practica el alfabeto de la Lengua de Señas Colombiana (LSC) usando la cámara de tu dispositivo, en tiempo real."
  },
  {
    titulo: "Aprende el alfabeto",
    descripcion:
      "En la sección \"Aprender\" encuentras cada letra del alfabeto LSC con su descripción y ejemplo visual."
  },
  {
    titulo: "Practica con tu cámara",
    descripcion:
      "En \"Practicar señas\" tu cámara reconoce tus señas en tiempo real y te dice si acertaste."
  },
  {
    titulo: "Revisa tu progreso",
    descripcion:
      "En \"Mi perfil\" puedes ver cuántas letras has dominado y tu porcentaje de avance."
  }
];

function Bienvenida({ onCerrar }: Props) {
  const [pasoActual, setPasoActual] = useState(0);

  const esUltimoPaso = pasoActual === pasos.length - 1;

  function irSiguiente() {
    if (esUltimoPaso) {
      onCerrar();
      return;
    }

    setPasoActual((actual) => actual + 1);
  }

  function irAnterior() {
    setPasoActual((actual) => Math.max(0, actual - 1));
  }

  const paso = pasos[pasoActual];

  return (
    <div className="overlayBienvenida" role="presentation">
      <div
        className="modalBienvenida"
        role="dialog"
        aria-modal="true"
        aria-labelledby="tituloBienvenida"
      >
        <button
          className="botonSaltar"
          onClick={onCerrar}
          aria-label="Saltar guía de bienvenida"
        >
          Saltar
        </button>

        <h2 id="tituloBienvenida">{paso.titulo}</h2>
        <p>{paso.descripcion}</p>

        <div className="pasosBienvenida">
          {pasos.map((_, indice) => (
            <span
              key={indice}
              className={
                indice === pasoActual
                  ? "puntoPaso puntoPasoActivo"
                  : "puntoPaso"
              }
            />
          ))}
        </div>

        <div className="botonesBienvenida">
          <button onClick={irAnterior} disabled={pasoActual === 0}>
            Atrás
          </button>

          <button onClick={irSiguiente}>
            {esUltimoPaso ? "Comenzar" : "Siguiente"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Bienvenida;