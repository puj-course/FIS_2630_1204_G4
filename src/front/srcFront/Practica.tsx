import { useEffect, useState } from "react";

import { ErrorApi } from "./services/api";
import {
  obtenerLetras,
  type Letra
} from "./services/letras";


function Practica() {
  const [letras, setLetras] = useState<Letra[]>([]);
  const [letraSeleccionada, setLetraSeleccionada] =
    useState<Letra | null>(null);
  const [cargando, setCargando] = useState(true);
  const [mensajeError, setMensajeError] = useState("");

  useEffect(() => {
    let componenteActivo = true;

    async function cargarLetras() {
      try {
        const datos = await obtenerLetras();

        if (!componenteActivo) {
          return;
        }

        setLetras(datos);
        setLetraSeleccionada(datos[0] ?? null);

      } catch (error) {
        if (!componenteActivo) {
          return;
        }

        setMensajeError(
          error instanceof ErrorApi
            ? error.message
            : "No fue posible cargar las letras."
        );

      } finally {
        if (componenteActivo) {
          setCargando(false);
        }
      }
    }

    void cargarLetras();

    return () => {
      componenteActivo = false;
    };
  }, []);

  const letraActual = letraSeleccionada?.letra ?? "-";

  return (
    <div className="practica">
      <section className="practicaHeader">
        <div>
          <h1>
            Alfabeto: Letra {letraActual}
          </h1>
          <p>
            Posiciona tu mano frente a la cámara para practicar.
          </p>
        </div>

        <button type="button">
          Apagar cámara
        </button>
      </section>

      <section className="zonaPracti">
        <div className="camara">
          <div className="estadoCamara">
            Grabando
          </div>

          <div className="deteccion">
            Detectando mano...
          </div>
        </div>

        <div className="panelPractica">
          <div className="objetivo">
            <h3>Objetivo</h3>
            <strong>{letraActual}</strong>
            <p>Precisión</p>

            <div className="barra">
              <div></div>
            </div>
          </div>

          <div className="instrucciones">
            <h2>Información de la letra</h2>

            {cargando ? (
              <p>Cargando información...</p>
            ) : letraSeleccionada ? (
              <p>
                {letraSeleccionada.descripcion
                  ?? "Esta letra no tiene una descripción registrada."}
              </p>
            ) : (
              <p>No hay una letra seleccionada.</p>
            )}
          </div>
        </div>
      </section>

      <section className="alfabeto">
        <h3>Navegador alfabeto</h3>

        {cargando && (
          <p role="status">Cargando letras...</p>
        )}

        {!cargando && mensajeError && (
          <p role="alert">{mensajeError}</p>
        )}

        {!cargando
          && !mensajeError
          && letras.length === 0 && (
            <p>No hay letras registradas.</p>
          )}

        {letras.map((letra) => (
          <button
            key={letra.id_letra}
            type="button"
            className={
              letraSeleccionada?.id_letra === letra.id_letra
                ? "letraActiva"
                : undefined
            }
            aria-pressed={
              letraSeleccionada?.id_letra === letra.id_letra
            }
            onClick={() => setLetraSeleccionada(letra)}
          >
            {letra.letra}
          </button>
        ))}
      </section>
    </div>
  );
}

export default Practica;