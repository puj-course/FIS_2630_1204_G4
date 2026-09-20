import "./Practica.css";
import { useEffect, useState } from "react";

import { ErrorApi } from "./services/api";
import {
  obtenerLetras,
  type Letra
} from "./services/letras";

import Camara from "./components/Camara";
import { useCamara } from "./hooks/useCamara";

import ResultadoReconocimiento from "./components/ResultadoReconocimiento";



function Practica() {
    const {
    videoRef,
    estado: estadoCamara,
    mensajeError: errorCamara,
    iniciarCamara,
    detenerCamara,
  } = useCamara();

  const camaraActiva = estadoCamara === "activa";
  const solicitandoCamara = estadoCamara === "solicitando";

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
          <h1>Alfabeto: Letra {letraActual}</h1>
          <p>
            Posiciona tu mano frente a la cámara para practicar.
          </p>
        </div>

        <button
          type="button"
          onClick={() => {
            if (camaraActiva || solicitandoCamara) {
              detenerCamara();
            } else {
              void iniciarCamara();
            }
          }}
        >
          {solicitandoCamara
            ? "Cancelar"
            : camaraActiva
              ? "Apagar cámara"
              : "Activar cámara"}
        </button>
      </section>


      <section className="zonaPracti">
        <Camara
          videoRef={videoRef}
          activa={camaraActiva}
          solicitando={solicitandoCamara}
          mensajeError={errorCamara}
        />



        <div className="panelPractica">
          <div className="objetivo">
            <h3>Objetivo</h3>
            <strong>{letraActual}</strong>

            {camaraActiva ? (
              <ResultadoReconocimiento
  key={letraSeleccionada?.id_letra ?? "sin-letra"}
  videoRef={videoRef}
  idLetraObjetivo={
    letraSeleccionada?.id_letra ?? null
  }
/>
            ) : (
              <p>
                Activa la cámara para iniciar el reconocimiento.
              </p>
            )}
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