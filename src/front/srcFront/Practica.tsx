import "./Practica.css";
import { useEffect, useState } from "react";
import {
  FaVideo,
  FaBullseye,
  FaHistory,
} from "react-icons/fa";

import { ErrorApi } from "./services/api";
import {
  obtenerLetras,
  type Letra,
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

  const textoEstadoCamara = solicitandoCamara
    ? "Solicitando cámara"
    : camaraActiva
      ? "Cámara activa"
      : "Cámara inactiva";

  const alternarCamara = () => {
    if (camaraActiva || solicitandoCamara) {
      detenerCamara();
    } else {
      void iniciarCamara();
    }
  };

  return (
    <div className="practica">
      <header className="practicaHeader">
        <div className="tituloPractica">
          <div className="tituloPracticaPrincipal">
            <h1>Práctica Libre</h1>
            <span className="etiquetaVision">
              LSC en vivo
            </span>
          </div>

          <p>
            Practica el alfabeto de la Lengua de Señas Colombiana
            con visión por computadora.
          </p>
        </div>

        <button
          type="button"
          className={
            camaraActiva
              ? "botonCamara botonCamaraActiva"
              : "botonCamara"
          }
          onClick={alternarCamara}
        >
          <FaVideo />

          {solicitandoCamara
            ? "Cancelar"
            : camaraActiva
              ? "Apagar cámara"
              : "Activar cámara"}
        </button>
      </header>

      {!cargando && mensajeError && (
        <div
          className="mensajeErrorPractica"
          role="alert"
        >
          {mensajeError}
        </div>
      )}

      <section className="zonaPracticaNueva">
        <div className="columnaCamara">
          <div className="contenedorCamaraPractica">
            <div className="barraSuperiorCamara">
              <span
                className={
                  camaraActiva
                    ? "estadoCamaraBadge estadoCamaraActivo"
                    : "estadoCamaraBadge"
                }
              >
                <span className="puntoEstado"></span>
                {textoEstadoCamara}
              </span>
            </div>

            <Camara
              videoRef={videoRef}
              activa={camaraActiva}
              solicitando={solicitandoCamara}
              mensajeError={errorCamara}
            />
          </div>
        </div>

        <aside className="columnaAnalisis">
          <section className="panelAnalisis">
            <div className="tituloPanelAnalisis">
              <FaBullseye />
              <h2>Análisis en tiempo real</h2>
            </div>

            <div className="resultadoPractica">
              {camaraActiva ? (
                <ResultadoReconocimiento
                  key={
                    letraSeleccionada?.id_letra ??
                    "sin-letra"
                  }
                  videoRef={videoRef}
                  idLetraObjetivo={
                    letraSeleccionada?.id_letra ?? null
                  }
                />
              ) : (
                <div className="reconocimientoInactivo">
                  <FaVideo />
                  <p>
                    Activa la cámara para iniciar el reconocimiento.
                  </p>
                </div>
              )}
            </div>
          </section>

          <section className="panelUltimasSenas">
            <div className="tituloUltimasSenas">
              <div>
                <FaHistory />
                <h2>
                  Últimas señas reconocidas
                </h2>
              </div>

              <span>
                Historial
              </span>
            </div>

            <div className="historialReconocimientoVacio">
              <FaHistory />

              <p>
                Las señas reconocidas durante la práctica
                aparecerán aquí.
              </p>
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}

export default Practica;