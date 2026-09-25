import "./Practica.css";
import {
  useCallback,
  useEffect,
  useState,
} from "react";
import {
  FaVideo,
  FaBullseye,
  FaHistory,
} from "react-icons/fa";
import { ErrorApi } from "./services/api";
import { obtenerSesion } from "./services/autenticacion";
import {
  obtenerLetras,
  type Letra,
} from "./services/letras";
import {
  consultarResultadosReconocimiento,
  type ResultadoRegistrado,
} from "./services/resultados";
import Camara from "./components/Camara";
import { useCamara } from "./hooks/useCamara";
import ResultadoReconocimiento from "./components/ResultadoReconocimiento";
import type {
  ModoReconocimiento,
} from "./services/vision";

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

  const [letraSeleccionada, setLetraSeleccionada] =
    useState<Letra | null>(null);

  const [historial, setHistorial] =
    useState<ResultadoRegistrado[]>([]);

  const [cargando, setCargando] = useState(true);
  const [cargandoHistorial, setCargandoHistorial] =
    useState(true);

  const [mensajeError, setMensajeError] = useState("");
  const [errorHistorial, setErrorHistorial] = useState("");

  const [modo, setModo] =
    useState<ModoReconocimiento>("estatica");

  const cargarHistorial = useCallback(async () => {
    const sesion = obtenerSesion();

    if (!sesion) {
      setHistorial([]);
      setCargandoHistorial(false);
      return;
    }

    setCargandoHistorial(true);

    try {
      const respuesta =
        await consultarResultadosReconocimiento(
          sesion.access_token
        );

      setHistorial(
        respuesta.resultados.slice(0, 5)
      );

      setErrorHistorial("");
    } catch (error) {
      setErrorHistorial(
        error instanceof ErrorApi
          ? error.message
          : "No fue posible cargar el historial."
      );
    } finally {
      setCargandoHistorial(false);
    }
  }, []);

  useEffect(() => {
    let componenteActivo = true;

    async function cargarLetras() {
      try {
        const datos = await obtenerLetras();

        if (!componenteActivo) {
          return;
        }

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
    void cargarHistorial();

    return () => {
      componenteActivo = false;
    };
  }, [cargarHistorial]);

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

  const manejarReconocimientoCorrecto = (
    idLetra: number
  ) => {
    if (
      letraSeleccionada
      && letraSeleccionada.id_letra === idLetra
    ) {
      console.log(
        "Letra reconocida correctamente:",
        idLetra
      );
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

              <h2>
                Análisis en tiempo real
              </h2>
            </div>

            <div
              className="selectorModoReconocimiento"
              role="group"
              aria-label="Tipo de reconocimiento"
            >
              <button
                type="button"
                className={
                  modo === "estatica"
                    ? "modoReconocimientoActivo"
                    : undefined
                }
                aria-pressed={modo === "estatica"}
                onClick={() => setModo("estatica")}
              >
                Letra estática
              </button>

              <button
                type="button"
                className={
                  modo === "movimiento"
                    ? "modoReconocimientoActivo"
                    : undefined
                }
                aria-pressed={modo === "movimiento"}
                onClick={() => setModo("movimiento")}
              >
                Letra con movimiento
              </button>
            </div>

            <div className="resultadoPractica">
              {camaraActiva ? (
                <ResultadoReconocimiento
                  key={`${letraSeleccionada?.id_letra ?? "sin-letra"}-${modo}`}
                  videoRef={videoRef}
                  idLetraObjetivo={
                    letraSeleccionada?.id_letra ?? null
                  }
                  modo={modo}
                  onReconocimientoCorrecto={
                    manejarReconocimientoCorrecto
                  }
                  onResultadoRegistrado={() => {
                    void cargarHistorial();
                  }}
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

            {cargandoHistorial ? (
              <div className="historialReconocimientoVacio">
                <p>
                  Cargando historial...
                </p>
              </div>
            ) : errorHistorial ? (
              <div className="historialReconocimientoVacio">
                <p role="alert">
                  {errorHistorial}
                </p>
              </div>
            ) : historial.length === 0 ? (
              <div className="historialReconocimientoVacio">
                <FaHistory />

                <p>
                  Aún no tienes intentos registrados.
                </p>
              </div>
            ) : (
              <div className="listaHistorialReconocimiento">
                {historial.map((resultado) => (
                  <div
                    className={
                      resultado.es_correcto
                        ? "itemHistorialReconocimiento historialCorrecto"
                        : "itemHistorialReconocimiento historialIncorrecto"
                    }
                    key={resultado.id_resultado}
                  >
                    <div className="letraHistorial">
                      {resultado.letra_detectada}
                    </div>

                    <div className="detalleHistorial">
                      <strong>
                        {resultado.es_correcto
                          ? "Seña correcta"
                          : "Seña incorrecta"}
                      </strong>

                      <span>
                        Detectada: {resultado.letra_detectada}
                      </span>
                    </div>

                    <div className="confianzaHistorial">
                      {Math.round(
                        resultado.confianza * 100
                      )}%
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </aside>
      </section>
    </div>
  );
}

export default Practica;