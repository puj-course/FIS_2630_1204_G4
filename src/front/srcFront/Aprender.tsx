import { useState, useEffect } from "react";
import { obtenerSesion } from "./services/autenticacion";
import { obtenerLetras, actualizarLetra, type Letra as LetraBackend } from "./services/letras";
import { ErrorApi } from "./services/api";

import imagenA from "./assets/señas/LETRA A.jpg";
import imagenB from "./assets/señas/LETRA B.jpg";
import imagenC from "./assets/señas/LETRA C.jpg";
import imagenD from "./assets/señas/LETRA D.jpg";
import imagenE from "./assets/señas/LETRA E.jpg";
import imagenF from "./assets/señas/LETRA F.jpg";
import imagenG from "./assets/señas/LETRA G.jpg";
import imagenH from "./assets/señas/LETRA H.jpg";
import imagenI from "./assets/señas/LETRA I.jpg";
import imagenJ from "./assets/señas/LETRA J.jpg";
import imagenK from "./assets/señas/LETRA K.jpg";
import imagenL from "./assets/señas/LETRA L.jpg";
import imagenM from "./assets/señas/LETRA M.jpg";
import imagenN from "./assets/señas/LETRA N.jpg";
import imagenÑ from "./assets/señas/LETRA Ñ.jpg";
import imagenO from "./assets/señas/LETRA O.jpg";
import imagenP from "./assets/señas/LETRA P.jpg";
import imagenQ from "./assets/señas/LETRA Q.jpg";
import imagenR from "./assets/señas/LETRA R.jpg";
import imagenS from "./assets/señas/LETRA S.jpg";
import imagenT from "./assets/señas/LETRA T.jpg";
import imagenU from "./assets/señas/LETRA U.jpg";
import imagenV from "./assets/señas/LETRA V.jpg";
import imagenW from "./assets/señas/LETRA W.jpg";
import imagenX from "./assets/señas/LETRA X.jpg";
import imagenY from "./assets/señas/LETRA Y.jpg";
import imagenZ from "./assets/señas/LETRA Z.jpg";

interface Props {
  cambiarPagina: (pagina: string) => void;
}

const imagenesLocales: Record<string, string> = {
  A: imagenA, B: imagenB, C: imagenC, D: imagenD, E: imagenE,
  F: imagenF, G: imagenG, H: imagenH, I: imagenI, J: imagenJ,
  K: imagenK, L: imagenL, M: imagenM, N: imagenN, "Ñ": imagenÑ,
  O: imagenO, P: imagenP, Q: imagenQ, R: imagenR, S: imagenS,
  T: imagenT, U: imagenU, V: imagenV, W: imagenW, X: imagenX,
  Y: imagenY, Z: imagenZ,
};

function Aprender({ cambiarPagina }: Props) {
  const [letrasBackend, setLetrasBackend] = useState<LetraBackend[]>([]);
  const [letraSeleccionada, setLetraSeleccionada] = useState<LetraBackend | null>(null);
  const [cargando, setCargando] = useState(true);
  const [mensajeCarga, setMensajeCarga] = useState("");

  const [editando, setEditando] = useState(false);
  const [descripcionEditada, setDescripcionEditada] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");
  const [mensajeExito, setMensajeExito] = useState("");

  const sesion = obtenerSesion();
  const esAdministrador = sesion?.usuario.rol === "administrador";
  const [errorImagenRemota, setErrorImagenRemota] = useState(false);

  useEffect(() => {
    cargarLetras();
  }, []);

  const cargarLetras = async () => {
    setCargando(true);
    setMensajeCarga("");
    try {
      const resultado = await obtenerLetras();
      setLetrasBackend(resultado);
    } catch {
      setMensajeCarga("No fue posible cargar el alfabeto en este momento");
    } finally {
      setCargando(false);
    }
  };

  const seleccionarLetra = (letra: LetraBackend) => {
    setLetraSeleccionada(letra);
    setEditando(false);
    setMensajeError("");
    setMensajeExito("");
    setErrorImagenRemota(false);
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
        { descripcion: descripcionEditada },
        sesion.access_token
      );

      setLetrasBackend((previas) =>
        previas.map((l) => (l.id_letra === resultado.letra.id_letra ? resultado.letra : l))
      );
      setLetraSeleccionada(resultado.letra);
      setMensajeExito("Cambios guardados correctamente");
      setEditando(false);
    } catch (error) {
      setMensajeError(
        error instanceof ErrorApi ? error.message : "No fue posible guardar los cambios"
      );
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="aprender">
      <h1>Aprender LSC</h1>
      {!cargando && !mensajeCarga && letrasBackend.length > 0 && (
        <p>Selecciona una letra para conocer su representación en lengua de señas.</p>
      )}

      {cargando && <p role="status">Cargando alfabeto...</p>}

      {!cargando && mensajeCarga && (
        <div className="mensajeError" role="alert">
          <p>{mensajeCarga}</p>
        </div>
      )}

      {!cargando && !mensajeCarga && letrasBackend.length === 0 && (
        <div className="mensajeSinLetras" role="status">
          <h2>No hay letras disponibles por el momento</h2>
          <p>Cuando se agreguen letras al alfabeto, aparecerán en esta sección.</p>
        </div>
      )}

      {!cargando && !mensajeCarga && letrasBackend.length > 0 && (
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

      {!cargando && !mensajeCarga && letrasBackend.length > 0 && letraSeleccionada && (
        <section className="detalleLetra">
          <h2>Letra {letraSeleccionada.letra}</h2>

          <div className="imagenSena">
            {letraSeleccionada.ruta_imagen && !errorImagenRemota ? (
              <img
                src={letraSeleccionada.ruta_imagen}
                alt={`Seña letra ${letraSeleccionada.letra}`}
                onError={() => setErrorImagenRemota(true)}
              />
            ) : imagenesLocales[letraSeleccionada.letra.toUpperCase().trim()] ? (
              <img
                src={imagenesLocales[letraSeleccionada.letra.toUpperCase().trim()]}
                alt={`Seña letra ${letraSeleccionada.letra}`}
              />
            ) : (
              <p>Imagen de la seña</p>
            )}
          </div>
          {!editando && <p>{letraSeleccionada.descripcion}</p>}

          {esAdministrador && editando && (
            <div className="editorDescripcion">
              <textarea
                value={descripcionEditada}
                onChange={(e) => setDescripcionEditada(e.target.value)}
                rows={4}
              />
              {mensajeError && <p className="mensaje-error">{mensajeError}</p>}
              {mensajeExito && <p className="mensaje-exito">{mensajeExito}</p>}
              <div className="accionesEdicion">
                <button onClick={guardarCambios} disabled={guardando}>
                  {guardando ? "Guardando..." : "Guardar cambios"}
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
            <button className="botonPracticar" onClick={() => cambiarPagina("practica")}>
              Practicar esta letra
            </button>

            {esAdministrador && !editando && (
              <button className="botonEditar" onClick={iniciarEdicion}>
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
