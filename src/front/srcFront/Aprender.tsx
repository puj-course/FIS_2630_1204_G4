import { useState, useEffect } from "react";
import { obtenerSesion } from "./services/autenticacion";
import {
  obtenerLetras,
  actualizarLetra,
  type Letra as LetraBackend,
} from "./services/letras";
import { ErrorApi } from "./services/api";

interface Props {
  cambiarPagina: (pagina: string) => void;
}

const API_URL = "http://localhost:8000";

function Aprender({ cambiarPagina }: Props) {
  const [letrasBackend, setLetrasBackend] = useState<LetraBackend[]>([]);
  const [letraSeleccionada, setLetraSeleccionada] =
    useState<LetraBackend | null>(null);

  const [cargando, setCargando] = useState(true);
  const [mensajeCarga, setMensajeCarga] = useState("");

  const [editando, setEditando] = useState(false);
  const [descripcionEditada, setDescripcionEditada] = useState("");

  const [guardando, setGuardando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");
  const [mensajeExito, setMensajeExito] = useState("");

  const sesion = obtenerSesion();
  const esAdministrador = sesion?.usuario.rol === "administrador";


  useEffect(() => {
    let activo = true;

    const cargarLetras = async () => {
      try {
        const resultado = await obtenerLetras();

        if (activo) {
          setLetrasBackend(resultado);
        }
      } catch {
        if (activo) {
          setMensajeCarga(
            "No fue posible cargar el alfabeto en este momento"
          );
        }
      } finally {
        if (activo) {
          setCargando(false);
        }
      }
    };

    void cargarLetras();

    return () => {
      activo = false;
    };
  }, []);


  const seleccionarLetra = (letra: LetraBackend) => {
    setLetraSeleccionada(letra);
    setEditando(false);
    setMensajeError("");
    setMensajeExito("");
  };


  const iniciarEdicion = () => {
    if (!letraSeleccionada) return;

    setDescripcionEditada(letraSeleccionada.descripcion ?? "");
    setEditando(true);
    setMensajeExito("");
  };


  const guardarCambios = async () => {
    if (!letraSeleccionada || !sesion) return;

    setGuardando(true);
    setMensajeError("");
    setMensajeExito("");

    try {
      const resultado = await actualizarLetra(
        letraSeleccionada.id_letra,
        {
          descripcion: descripcionEditada,
        },
        sesion.access_token
      );

      setLetrasBackend((previas) =>
        previas.map((letra) =>
          letra.id_letra === resultado.letra.id_letra
            ? resultado.letra
            : letra
        )
      );

      setLetraSeleccionada(resultado.letra);
      setMensajeExito("Cambios guardados correctamente");
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
      <h1>Aprender LSC</h1>


      {!cargando &&
        !mensajeCarga &&
        letrasBackend.length > 0 && (
          <p>
            Selecciona una letra para conocer su representación en lengua
            de señas.
          </p>
        )}


      {cargando && (
        <p role="status">
          Cargando alfabeto...
        </p>
      )}


      {!cargando && mensajeCarga && (
        <div className="mensajeError" role="alert">
          <p>{mensajeCarga}</p>
        </div>
      )}


      {!cargando &&
        !mensajeCarga &&
        letrasBackend.length === 0 && (
          <div className="mensajeSinLetras" role="status">
            <h2>No hay letras disponibles por el momento</h2>
            <p>
              Cuando se agreguen letras al alfabeto, aparecerán en esta
              sección.
            </p>
          </div>
        )}


      {!cargando &&
        !mensajeCarga &&
        letrasBackend.length > 0 && (
          <div className="contenedorLetras">
            {letrasBackend.map((letra) => (
              <button
                key={letra.id_letra}
                className={
                  letraSeleccionada?.id_letra === letra.id_letra
                    ? "letraActiva"
                    : "letraBox"
                }
                onClick={() => seleccionarLetra(letra)}
              >
                {letra.letra}
              </button>
            ))}
          </div>
        )}


      {!cargando &&
        !mensajeCarga &&
        letrasBackend.length > 0 &&
        letraSeleccionada && (
          <section className="detalleLetra">

            <h2>
              Letra {letraSeleccionada.letra}
            </h2>


            <div className="imagenSena">
  {letraSeleccionada.ruta_imagen ? (
    <img
      src={`${API_URL}${letraSeleccionada.ruta_imagen}`}
      alt={`Seña letra ${letraSeleccionada.letra}`}
    />
  ) : (
    <p>
      Imagen no disponible
    </p>
  )}
</div>


            {!editando && (
              <p>
                {letraSeleccionada.descripcion}
              </p>
            )}


            {esAdministrador && editando && (
              <div className="editorDescripcion">

                <textarea
                  value={descripcionEditada}
                  onChange={(e) =>
                    setDescripcionEditada(e.target.value)
                  }
                  rows={4}
                />

                {mensajeError && (
                  <p className="mensaje-error">
                    {mensajeError}
                  </p>
                )}

                {mensajeExito && (
                  <p className="mensaje-exito">
                    {mensajeExito}
                  </p>
                )}


                <div className="accionesEdicion">

                  <button
                    onClick={guardarCambios}
                    disabled={guardando}
                  >
                    {guardando
                      ? "Guardando..."
                      : "Guardar cambios"}
                  </button>


                  <button
                    className="botonCancelar"
                    onClick={() => setEditando(false)}
                    disabled={guardando}
                  >
                    Cancelar
                  </button>

                </div>

              </div>
            )}


            <div className="accionesLetra">

              <button
                className="botonPracticar"
                onClick={() => cambiarPagina("practica")}
              >
                Practicar esta letra
              </button>


              {esAdministrador && !editando && (
                <button
                  className="botonEditar"
                  onClick={iniciarEdicion}
                >
                  Editar instrucciones
                </button>
              )}

            </div>

          </section>
        )}

    </div>
  );
}

export default Aprender;