import "./Aprender.css";
import { useState, useEffect } from "react";
import { obtenerSesion } from "./services/autenticacion";
import {
  obtenerLetras,
  actualizarLetra,
  type Letra as LetraBackend,
} from "./services/letras";
import {
  consultarEstadoLetras,
  type EstadoAprendizaje,
} from "./services/progreso";
import { ErrorApi } from "./services/api";

interface Props {
  cambiarPagina: (
    pagina: string,
    idLetra?: number
  ) => void;
}

const API_URL = "http://localhost:8000";

function Aprender({ cambiarPagina }: Props) {
  const [letrasBackend, setLetrasBackend] =
    useState<LetraBackend[]>([]);

  const [estadosAprendizaje, setEstadosAprendizaje] =
    useState<Record<number, EstadoAprendizaje>>({});

  const [letraSeleccionada, setLetraSeleccionada] =
    useState<LetraBackend | null>(null);

  const [cargando, setCargando] = useState(true);
  const [errorCarga, setErrorCarga] = useState("");
  const [errorProgreso, setErrorProgreso] = useState("");
  const [editando, setEditando] = useState(false);
  const [descripcionEditada, setDescripcionEditada] =
    useState("");
  const [guardando, setGuardando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");
  const [mensajeExito, setMensajeExito] = useState("");

  const sesion = obtenerSesion();
  const esAdministrador =
    sesion?.usuario.rol === "administrador";

  useEffect(() => {
    let activo = true;

    const cargarInformacion = async () => {
      try {
        const resultadoLetras = await obtenerLetras();

        if (!activo) {
          return;
        }

        setLetrasBackend(resultadoLetras);
        setErrorCarga("");

        const sesionActual = obtenerSesion();

        if (sesionActual) {
          try {
            const resultadoProgreso =
              await consultarEstadoLetras(
                sesionActual.access_token
              );

            if (!activo) {
              return;
            }

            const nuevosEstados: Record<
              number,
              EstadoAprendizaje
            > = {};

            resultadoProgreso.letras.forEach((letra) => {
              nuevosEstados[letra.id_letra] =
                letra.estado;
            });

            setEstadosAprendizaje(nuevosEstados);
            setErrorProgreso("");
          } catch (error) {
            if (!activo) {
              return;
            }

            setErrorProgreso(
              error instanceof ErrorApi
                ? error.message
                : "No fue posible consultar el estado de aprendizaje."
            );
          }
        }
      } catch (error) {
        if (!activo) {
          return;
        }

        setErrorCarga(
          error instanceof ErrorApi
            ? error.message
            : "No fue posible cargar el alfabeto en este momento"
        );
      } finally {
        if (activo) {
          setCargando(false);
        }
      }
    };

    void cargarInformacion();

    return () => {
      activo = false;
    };
  }, []);

  const seleccionarLetra = (
    letra: LetraBackend
  ) => {
    setLetraSeleccionada(letra);
    setEditando(false);
    setMensajeError("");
    setMensajeExito("");
  };

  const cerrarModal = () => {
    setLetraSeleccionada(null);
    setEditando(false);
    setMensajeError("");
    setMensajeExito("");
  };

  const cambiarLetra = (
    direccion: number
  ) => {
    if (!letraSeleccionada) {
      return;
    }

    const indiceActual =
      letrasBackend.findIndex(
        (letra) =>
          letra.id_letra ===
          letraSeleccionada.id_letra
      );

    const nuevoIndice =
      indiceActual + direccion;

    if (
      nuevoIndice < 0
      || nuevoIndice >= letrasBackend.length
    ) {
      return;
    }

    setLetraSeleccionada(
      letrasBackend[nuevoIndice]
    );

    setEditando(false);
    setMensajeError("");
    setMensajeExito("");
  };

  const indiceLetraSeleccionada =
    letraSeleccionada
      ? letrasBackend.findIndex(
          (letra) =>
            letra.id_letra ===
            letraSeleccionada.id_letra
        )
      : -1;

  const iniciarEdicion = () => {
    if (!letraSeleccionada) {
      return;
    }

    setDescripcionEditada(
      letraSeleccionada.descripcion ?? ""
    );

    setEditando(true);
    setMensajeError("");
    setMensajeExito("");
  };

  const guardarCambios = async () => {
    if (
      !letraSeleccionada
      || !sesion
    ) {
      return;
    }

    setGuardando(true);
    setMensajeError("");
    setMensajeExito("");

    try {
      const resultado =
        await actualizarLetra(
          letraSeleccionada.id_letra,
          {
            descripcion:
              descripcionEditada,
          },
          sesion.access_token
        );

      setLetrasBackend((previas) =>
        previas.map((letra) =>
          letra.id_letra ===
          resultado.letra.id_letra
            ? resultado.letra
            : letra
        )
      );

      setLetraSeleccionada(
        resultado.letra
      );

      setMensajeExito(
        "Cambios guardados correctamente"
      );

      setEditando(false);
    } catch (error) {
      setMensajeError(
        error instanceof ErrorApi
          ? error.message
          : "No fue posible guardar los cambios"
      );
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="aprender">
      <div className="cabeceraModulo">
        <div>
          <h1>
            Módulo de aprendizaje
          </h1>

          <p>
            Explora las letras fundamentales
            de la Lengua de Señas Colombiana.
          </p>
        </div>
      </div>

      <div className="informacionModulo">
        <div className="iconoInformacion">
          ✋
        </div>

        <div>
          <h2>
            Alfabeto de la Lengua de Señas
            Colombiana
          </h2>

          <p>
            Selecciona una letra para conocer
            su representación, revisar sus
            instrucciones y comenzar a practicar.
          </p>
        </div>
      </div>

      {cargando && (
        <div
          className="estadoAprender"
          role="status"
        >
          <p>
            Cargando alfabeto...
          </p>
        </div>
      )}

      {!cargando && errorCarga && (
        <div
          className="mensajeError"
          role="alert"
        >
          <p>
            {errorCarga}
          </p>
        </div>
      )}

      {!cargando
        && !errorCarga
        && errorProgreso && (
          <div
            className="mensajeErrorProgreso"
            role="alert"
          >
            <p>
              {errorProgreso}
            </p>
          </div>
        )}

      {!cargando
        && !errorCarga
        && letrasBackend.length === 0 && (
          <div
            className="mensajeSinLetras"
            role="status"
          >
            <h2>
              No hay letras disponibles por el
              momento
            </h2>

            <p>
              Cuando se agreguen letras al
              alfabeto, aparecerán en esta
              sección.
            </p>
          </div>
        )}

      {!cargando
        && !errorCarga
        && letrasBackend.length > 0 && (
          <section className="contenidoAprendizaje">
            <div className="encabezadoAlfabeto">
              <div>
                <h2>
                  Alfabeto LSC
                </h2>

                <p>
                  Conoce cada seña y revisa tu
                  progreso de aprendizaje.
                </p>
              </div>
            </div>

            <div className="gridLetras">
              {letrasBackend.map((letra) => {
                const estado =
                  estadosAprendizaje[
                    letra.id_letra
                  ] ?? "pendiente";

                return (
                  <article
                    className={`tarjetaLetra ${
                      estado === "aprendida"
                        ? "tarjetaLetraAprendida"
                        : "tarjetaLetraPendiente"
                    }`}
                    key={letra.id_letra}
                  >
                    <div className="cabeceraTarjetaLetra">
                      <span className="identificadorLetra">
                        {letra.letra}
                      </span>

                      <span
                        className={`estadoAprendizaje ${
                          estado === "aprendida"
                            ? "estadoAprendido"
                            : "estadoPendiente"
                        }`}
                      >
                        {estado === "aprendida"
                          ? "✓ Aprendida"
                          : "Pendiente"}
                      </span>
                    </div>

                    <div
                      className="vistaPreviaLetra"
                      onClick={() =>
                        seleccionarLetra(letra)
                      }
                    >
                      {letra.ruta_imagen ? (
                        <img
                          src={`${API_URL}${letra.ruta_imagen}`}
                          alt={`Seña letra ${letra.letra}`}
                        />
                      ) : (
                        <span className="letraSinImagen">
                          {letra.letra}
                        </span>
                      )}
                    </div>

                    <div className="contenidoTarjetaLetra">
                      <h3>
                        Letra {letra.letra}
                      </h3>

                      <p>
                        {letra.descripcion
                          || "Consulta cómo realizar esta seña correctamente."}
                      </p>
                    </div>

                    <div className="accionesTarjetaLetra">
                      <button
                        type="button"
                        className="botonGuia"
                        onClick={() =>
                          seleccionarLetra(letra)
                        }
                      >
                        Ver guía
                      </button>

                      <button
                        type="button"
                        className="botonPracticarTarjeta"
                        onClick={() =>
                          cambiarPagina(
                            "practica",
                            letra.id_letra
                          )
                        }
                      >
                        Practicar
                      </button>
                    </div>
                  </article>
                );
              })}
            </div>
          </section>
        )}

      {!cargando
        && !errorCarga
        && letrasBackend.length > 0
        && letraSeleccionada && (
          <div
            className="fondoModal"
            onClick={cerrarModal}
          >
            <div
              className="contenidoModal"
              onClick={(evento) =>
                evento.stopPropagation()
              }
            >
              <button
                type="button"
                className="flechaModal flechaAnterior"
                onClick={() =>
                  cambiarLetra(-1)
                }
                disabled={
                  indiceLetraSeleccionada === 0
                }
                aria-label="Letra anterior"
              >
                ‹
              </button>

              <section className="detalleLetra modalLetra">
                <button
                  className="cerrarModal"
                  type="button"
                  onClick={cerrarModal}
                  aria-label="Cerrar"
                >
                  ×
                </button>

                <h2>
                  Letra{" "}
                  {letraSeleccionada.letra}
                </h2>

                <div className="imagenSena">
                  {letraSeleccionada.ruta_imagen
                    ? (
                      <img
                        src={`${API_URL}${letraSeleccionada.ruta_imagen}`}
                        alt={`Seña letra ${letraSeleccionada.letra}`}
                      />
                    )
                    : (
                      <p>
                        Imagen no disponible
                      </p>
                    )}
                </div>

                {!editando && (
                  <p className="descripcionLetra">
                    {
                      letraSeleccionada.descripcion
                    }
                  </p>
                )}

                {mensajeExito
                  && !editando && (
                    <p className="mensaje-exito">
                      {mensajeExito}
                    </p>
                  )}

                {mensajeError
                  && !editando && (
                    <p className="mensaje-error">
                      {mensajeError}
                    </p>
                  )}

                {esAdministrador
                  && editando && (
                    <div className="editorDescripcion">
                      <textarea
                        value={
                          descripcionEditada
                        }
                        onChange={(evento) =>
                          setDescripcionEditada(
                            evento.target.value
                          )
                        }
                        rows={4}
                      />

                      {mensajeError && (
                        <p className="mensaje-error">
                          {mensajeError}
                        </p>
                      )}

                      <div className="accionesEdicion">
                        <button
                          type="button"
                          onClick={
                            guardarCambios
                          }
                          disabled={
                            guardando
                          }
                        >
                          {guardando
                            ? "Guardando..."
                            : "Guardar cambios"}
                        </button>

                        <button
                          type="button"
                          className="botonCancelar"
                          onClick={() =>
                            setEditando(false)
                          }
                          disabled={
                            guardando
                          }
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  )}

                <div className="accionesLetra">
                  <button
                    className="botonPracticar"
                    type="button"
                    onClick={() =>
                      cambiarPagina(
                        "practica",
                        letraSeleccionada.id_letra
                      )
                    }
                  >
                    Practicar esta letra
                  </button>

                  {esAdministrador
                    && !editando && (
                      <button
                        className="botonEditar"
                        type="button"
                        onClick={
                          iniciarEdicion
                        }
                      >
                        Editar instrucciones
                      </button>
                    )}
                </div>
              </section>

              <button
                type="button"
                className="flechaModal flechaSiguiente"
                onClick={() =>
                  cambiarLetra(1)
                }
                disabled={
                  indiceLetraSeleccionada
                  === letrasBackend.length - 1
                }
                aria-label="Siguiente letra"
              >
                ›
              </button>
            </div>
          </div>
        )}
    </div>
  );
}

export default Aprender;