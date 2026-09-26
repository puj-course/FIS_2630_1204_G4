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
  FaTrash,
} from "react-icons/fa";

import { ErrorApi } from "./services/api";
import { obtenerSesion } from "./services/autenticacion";

import {
  obtenerLetras,
  type Letra,
} from "./services/letras";

import {
  consultarResultadosReconocimiento,
  eliminarResultadosReconocimiento,
  type ResultadoRegistrado,
} from "./services/resultados";

import Camara from "./components/Camara";
import { useCamara } from "./hooks/useCamara";
import ResultadoReconocimiento from "./components/ResultadoReconocimiento";

import type {
  ModoReconocimiento,
} from "./services/vision";

interface Props {
  idLetraPractica?: number | null;
}

type ModalidadPractica =
  | "libre"
  | "especifica";

type LetraConNombre = Letra & {
  letra?: string;
  nombre?: string;
};

function obtenerNombreLetra(letra: Letra) {
  const letraConNombre =
    letra as LetraConNombre;

  return (
    letraConNombre.letra
    ?? letraConNombre.nombre
    ?? `Letra ${letra.id_letra}`
  );
}

function Practica({
  idLetraPractica = null,
}: Props) {
  const {
    videoRef,
    estado: estadoCamara,
    mensajeError: errorCamara,
    iniciarCamara,
    detenerCamara,
  } = useCamara();

  const camaraActiva =
    estadoCamara === "activa";

  const solicitandoCamara =
    estadoCamara === "solicitando";

  const [
    modalidadPractica,
    setModalidadPractica,
  ] = useState<ModalidadPractica | null>(
    idLetraPractica !== null
      ? "especifica"
      : null
  );

  const [
    letrasDisponibles,
    setLetrasDisponibles,
  ] = useState<Letra[]>([]);

  const [
    letraSeleccionada,
    setLetraSeleccionada,
  ] = useState<Letra | null>(null);

  const [historial, setHistorial] =
    useState<ResultadoRegistrado[]>([]);

  const [cargando, setCargando] =
    useState(true);

  const [
    cargandoHistorial,
    setCargandoHistorial,
  ] = useState(true);

  const [
    limpiandoHistorial,
    setLimpiandoHistorial,
  ] = useState(false);

  const [mensajeError, setMensajeError] =
    useState("");

  const [
    errorHistorial,
    setErrorHistorial,
  ] = useState("");

  const [modo, setModo] =
    useState<ModoReconocimiento>("estatica");

  const cargarHistorial =
    useCallback(async () => {
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
          respuesta.resultados
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

  const limpiarHistorial = async () => {
    const sesion = obtenerSesion();

    if (!sesion) {
      return;
    }

    const confirmar = window.confirm(
      "¿Seguro que deseas eliminar todo tu historial de reconocimiento?"
    );

    if (!confirmar) {
      return;
    }

    setLimpiandoHistorial(true);
    setErrorHistorial("");

    try {
      await eliminarResultadosReconocimiento(
        sesion.access_token
      );

      setHistorial([]);
    } catch (error) {
      setErrorHistorial(
        error instanceof ErrorApi
          ? error.message
          : "No fue posible limpiar el historial."
      );
    } finally {
      setLimpiandoHistorial(false);
    }
  };

  useEffect(() => {
    let componenteActivo = true;

    async function cargarLetras() {
      try {
        const datos =
          await obtenerLetras();

        if (!componenteActivo) {
          return;
        }

        setLetrasDisponibles(datos);

        if (idLetraPractica !== null) {
          const letraObjetivo =
            datos.find(
              (letra) =>
                letra.id_letra
                === idLetraPractica
            ) ?? null;

          setModalidadPractica(
            "especifica"
          );

          setLetraSeleccionada(
            letraObjetivo
          );

          if (!letraObjetivo) {
            setMensajeError(
              "No fue posible encontrar la letra seleccionada."
            );
          } else {
            setMensajeError("");
          }
        } else {
          setModalidadPractica(null);

          setLetraSeleccionada(
            datos[0] ?? null
          );

          setMensajeError("");
        }
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

    async function cargarHistorialInicial() {
      const sesion = obtenerSesion();

      if (!sesion) {
        await Promise.resolve();

        if (componenteActivo) {
          setHistorial([]);
          setCargandoHistorial(false);
        }

        return;
      }

      try {
        const respuesta =
          await consultarResultadosReconocimiento(
            sesion.access_token
          );

        if (!componenteActivo) {
          return;
        }

        setHistorial(
          respuesta.resultados
        );

        setErrorHistorial("");
      } catch (error) {
        if (!componenteActivo) {
          return;
        }

        setErrorHistorial(
          error instanceof ErrorApi
            ? error.message
            : "No fue posible cargar el historial."
        );
      } finally {
        if (componenteActivo) {
          setCargandoHistorial(false);
        }
      }
    }

    void cargarLetras();
    void cargarHistorialInicial();

    return () => {
      componenteActivo = false;
    };
  }, [idLetraPractica]);

  const textoEstadoCamara =
    solicitandoCamara
      ? "Solicitando cámara"
      : camaraActiva
        ? "Cámara activa"
        : "Cámara inactiva";

  const alternarCamara = () => {
    if (
      camaraActiva
      || solicitandoCamara
    ) {
      detenerCamara();
    } else {
      void iniciarCamara();
    }
  };

  const seleccionarPracticaLibre = () => {
    setLetraSeleccionada(null);
    setModalidadPractica("libre");
  };

  const seleccionarPracticaEspecifica =
    () => {
      if (!letraSeleccionada) {
        return;
      }

      setModalidadPractica("especifica");
    };

  const cambiarModalidad = () => {
    detenerCamara();

    setLetraSeleccionada(
      letrasDisponibles[0] ?? null
    );

    setModalidadPractica(null);
  };

  const manejarReconocimientoCorrecto = (
    idLetra: number
  ) => {
    if (
      modalidadPractica === "especifica"
      && (
        !letraSeleccionada
        || letraSeleccionada.id_letra
        !== idLetra
      )
    ) {
      return;
    }
  };

  if (
    idLetraPractica === null
    && modalidadPractica === null
  ) {
    return (
      <div className="practica">
        <section className="seleccionModalidadPractica">
          <div className="encabezadoSeleccionModalidad">
            <h1>
              ¿Cómo quieres practicar?
            </h1>

            <p>
              Elige una modalidad para comenzar
              tu práctica de Lengua de Señas
              Colombiana.
            </p>
          </div>

          {!cargando
            && mensajeError && (
              <div
                className="mensajeErrorPractica"
                role="alert"
              >
                {mensajeError}
              </div>
            )}

          <div className="opcionesModalidadPractica">
            <article className="opcionModalidadPractica">
              <FaVideo />

              <h2>
                Práctica libre
              </h2>

              <p>
                Activa la cámara y practica
                libremente cualquier letra del
                alfabeto.
              </p>

              <button
                type="button"
                onClick={
                  seleccionarPracticaLibre
                }
              >
                Iniciar práctica libre
              </button>
            </article>

            <article className="opcionModalidadPractica">
              <FaBullseye />

              <h2>
                Práctica específica
              </h2>

              <p>
                Selecciona una letra para
                concentrar el reconocimiento
                en ella.
              </p>

              <label
                htmlFor="letraPracticaEspecifica"
              >
                Letra para practicar
              </label>

              <select
                id="letraPracticaEspecifica"
                value={
                  letraSeleccionada?.id_letra
                  ?? ""
                }
                onChange={(evento) => {
                  const idLetra =
                    Number(
                      evento.target.value
                    );

                  const nuevaLetra =
                    letrasDisponibles.find(
                      (letra) =>
                        letra.id_letra
                        === idLetra
                    ) ?? null;

                  setLetraSeleccionada(
                    nuevaLetra
                  );
                }}
                disabled={
                  cargando
                  || letrasDisponibles.length
                    === 0
                }
              >
                {cargando ? (
                  <option value="">
                    Cargando letras...
                  </option>
                ) : letrasDisponibles.length
                  === 0 ? (
                    <option value="">
                      No hay letras disponibles
                    </option>
                  ) : (
                    letrasDisponibles.map(
                      (letra) => (
                        <option
                          key={letra.id_letra}
                          value={letra.id_letra}
                        >
                          {obtenerNombreLetra(
                            letra
                          )}
                        </option>
                      )
                    )
                  )}
              </select>

              <button
                type="button"
                onClick={
                  seleccionarPracticaEspecifica
                }
                disabled={
                  cargando
                  || !letraSeleccionada
                }
              >
                Iniciar práctica específica
              </button>
            </article>
          </div>
        </section>
      </div>
    );
  }

  const tituloPractica =
    modalidadPractica === "especifica"
      && letraSeleccionada
      ? `Práctica Específica: ${obtenerNombreLetra(
          letraSeleccionada
        )}`
      : "Práctica Libre";

  const descripcionPractica =
    modalidadPractica === "especifica"
      ? "Practica una letra específica de la Lengua de Señas Colombiana con visión por computadora."
      : "Practica libremente el alfabeto de la Lengua de Señas Colombiana con visión por computadora.";

  return (
    <div className="practica">
      <header className="practicaHeader">
        <div className="tituloPractica">
          <div className="tituloPracticaPrincipal">
            <h1>
              {tituloPractica}
            </h1>

            <span className="etiquetaVision">
              LSC en vivo
            </span>
          </div>

          <p>
            {descripcionPractica}
          </p>

          {idLetraPractica === null && (
            <button
              type="button"
              className="botonCambiarModalidad"
              onClick={cambiarModalidad}
            >
              Cambiar modalidad
            </button>
          )}
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

      {!cargando
        && mensajeError && (
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
              solicitando={
                solicitandoCamara
              }
              mensajeError={
                errorCamara
              }
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
                aria-pressed={
                  modo === "estatica"
                }
                onClick={() =>
                  setModo("estatica")
                }
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
                aria-pressed={
                  modo === "movimiento"
                }
                onClick={() =>
                  setModo("movimiento")
                }
              >
                Letra con movimiento
              </button>
            </div>

            <div className="resultadoPractica">
              {camaraActiva ? (
                <ResultadoReconocimiento
                  key={`${modalidadPractica}-${letraSeleccionada?.id_letra ?? "sin-letra"}-${modo}`}
                  videoRef={videoRef}
                  idLetraObjetivo={
                    modalidadPractica
                      === "especifica"
                      ? letraSeleccionada
                          ?.id_letra
                        ?? null
                      : null
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
                    Activa la cámara para
                    iniciar el reconocimiento.
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

              <button
                type="button"
                className="botonLimpiarHistorial"
                onClick={() =>
                  void limpiarHistorial()
                }
                disabled={
                  historial.length === 0
                  || limpiandoHistorial
                }
              >
                <FaTrash />

                {limpiandoHistorial
                  ? "Limpiando..."
                  : "Limpiar"}
              </button>
            </div>

            <div className="contenedorHistorialScroll">
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
                    Aún no tienes intentos
                    registrados.
                  </p>
                </div>
              ) : (
                <div className="listaHistorialReconocimiento">
                  {historial.map(
                    (resultado) => (
                      <div
                        className={
                          resultado.es_correcto
                            ? "itemHistorialReconocimiento historialCorrecto"
                            : "itemHistorialReconocimiento historialIncorrecto"
                        }
                        key={
                          resultado.id_resultado
                        }
                      >
                        <div className="letraHistorial">
                          {
                            resultado.letra_detectada
                          }
                        </div>

                        <div className="detalleHistorial">
                          <strong>
                            {resultado.es_correcto
                              ? "Seña correcta"
                              : "Seña incorrecta"}
                          </strong>

                          <span>
                            Detectada:{" "}
                            {
                              resultado.letra_detectada
                            }
                          </span>
                        </div>

                        <div className="confianzaHistorial">
                          {Math.round(
                            resultado.confianza
                            * 100
                          )}
                          %
                        </div>
                      </div>
                    )
                  )}
                </div>
              )}
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}

export default Practica;