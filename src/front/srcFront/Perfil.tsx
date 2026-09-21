import "./Perfil.css";
import { useEffect, useState } from "react";
import {
  FaUserCircle,
  FaVolumeUp,
  FaRegClone,
  FaBullseye,
  FaEnvelope,
  FaStar,
} from "react-icons/fa";
import { ErrorApi } from "./services/api";
import { obtenerSesion } from "./services/autenticacion";
import {
  consultarPerfil,
  type PerfilUsuario,
} from "./services/perfil";

function Perfil() {
  const [perfil, setPerfil] = useState<PerfilUsuario | null>(null);
  const [cargando, setCargando] = useState(true);
  const [mensajeError, setMensajeError] = useState("");
  const [sonido, setSonido] = useState(true);
  const [modoEspejo, setModoEspejo] = useState(true);
  const [metaDiaria, setMetaDiaria] = useState("10");

  useEffect(() => {
    let componenteActivo = true;

    async function cargarPerfil() {
      const sesion = obtenerSesion();

      if (!sesion) {
        if (componenteActivo) {
          setMensajeError("No se encontró una sesión activa.");
          setCargando(false);
        }
        return;
      }

      try {
        const perfilConsultado = await consultarPerfil(
          sesion.access_token
        );

        if (componenteActivo) {
          setPerfil(perfilConsultado);
        }
      } catch (error) {
        if (componenteActivo) {
          setMensajeError(
            error instanceof ErrorApi
              ? error.message
              : "No fue posible cargar el perfil."
          );
        }
      } finally {
        if (componenteActivo) {
          setCargando(false);
        }
      }
    }

    void cargarPerfil();

    return () => {
      componenteActivo = false;
    };
  }, []);

  if (cargando) {
    return (
      <div className="perfilVista estadoPerfil">
        <p>Cargando información del perfil...</p>
      </div>
    );
  }

  if (mensajeError || !perfil) {
    return (
      <div className="perfilVista estadoPerfil">
        <h2>No fue posible cargar el perfil</h2>
        <p role="alert">
          {mensajeError || "No se encontró información."}
        </p>
      </div>
    );
  }

  const porcentaje = Math.min(
    100,
    Math.max(0, perfil.progreso.porcentaje_progreso)
  );

  const precision =
    perfil.progreso.cantidad_intentos > 0
      ? (
          (perfil.progreso.cantidad_aciertos /
            perfil.progreso.cantidad_intentos) *
          100
        ).toFixed(0)
      : "0";

  const letrasPendientes = Math.max(
    0,
    perfil.progreso.total_letras -
      perfil.progreso.letras_dominadas
  );

  return (
    <div className="perfilVista">
      <div className="perfilTitulo">
        <h1>Perfil de Usuario</h1>
        <p>
          Administra tu cuenta, preferencias y progreso de aprendizaje
        </p>
      </div>

      <div className="perfilGrid">
        <section className="perfilResumen">
          <div className="perfilTarjetaUsuario">
            <div className="perfilAvatarContenedor">
              <div className="perfilAvatar">
                <FaUserCircle />
              </div>
              <span className="perfilEstado"></span>
            </div>

            <h2>{perfil.nombre}</h2>

            <p className="perfilCorreo">
              <FaEnvelope />
              {perfil.correo}
            </p>

            <span className="perfilNivel">
              <FaStar />
              {perfil.rol === "administrador"
                ? "Administrador"
                : "Estudiante"}
            </span>

            <div className="perfilEstadisticas">
              <div className="perfilDato">
                <small>Precisión Media</small>
                <strong>{precision}%</strong>
              </div>

              <div className="perfilDato">
                <small>Señas Dominadas</small>
                <strong>
                  {perfil.progreso.letras_dominadas}
                </strong>
              </div>
            </div>
          </div>
        </section>

        <section className="perfilPaneles">
          <div className="perfilPanel">
            <h3>Preferencias de la Cámara y Detección</h3>

            <div className="perfilOpcion">
              <div className="perfilOpcionInfo">
                <div className="perfilIcono">
                  <FaVolumeUp />
                </div>

                <div>
                  <strong>Efectos Sonoros</strong>
                  <p>
                    Reproduce tonos al reconocer señas correctamente
                  </p>
                </div>
              </div>

              <button
                type="button"
                className={
                  sonido
                    ? "switch switchActivo"
                    : "switch"
                }
                onClick={() => setSonido(!sonido)}
                aria-label="Activar o desactivar efectos sonoros"
              >
                <span></span>
              </button>
            </div>

            <div className="perfilOpcion">
              <div className="perfilOpcionInfo">
                <div className="perfilIcono">
                  <FaRegClone />
                </div>

                <div>
                  <strong>Modo Espejo</strong>
                  <p>
                    Invierte el video horizontalmente para una vista
                    más natural
                  </p>
                </div>
              </div>

              <button
                type="button"
                className={
                  modoEspejo
                    ? "switch switchActivo"
                    : "switch"
                }
                onClick={() => setModoEspejo(!modoEspejo)}
                aria-label="Activar o desactivar modo espejo"
              >
                <span></span>
              </button>
            </div>
          </div>
        </section>

        <section className="perfilPanel perfilMetaPanel">
          <h3>
            <FaBullseye />
            Meta Diaria de Práctica
          </h3>

          <p className="perfilMetaTexto">
            Selecciona cuántas señas quieres practicar cada día
          </p>

          <div className="perfilMetas">
            {["5", "10", "15", "20"].map((meta) => (
              <button
                key={meta}
                type="button"
                className={
                  metaDiaria === meta
                    ? "metaBoton metaActiva"
                    : "metaBoton"
                }
                onClick={() => setMetaDiaria(meta)}
              >
                {meta} señas / día
              </button>
            ))}
          </div>
        </section>
      </div>

      <section className="perfilProgreso">
        <div className="perfilProgresoEncabezado">
          <div>
            <h2>Progreso en el alfabeto LSC</h2>
            <p>
              Tu avance según las letras que has practicado y
              dominado.
            </p>
          </div>

          <strong>
            {porcentaje.toFixed(0)}%
          </strong>
        </div>

        <div
          className="perfilBarraProgreso"
          role="progressbar"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={porcentaje}
        >
          <div
            className="perfilBarraRelleno"
            style={{
              width: `${porcentaje}%`,
            }}
          ></div>
        </div>

        <div className="perfilResumenProgreso">
          <div>
            <span>Letras disponibles</span>
            <strong>
              {perfil.progreso.total_letras}
            </strong>
          </div>

          <div>
            <span>Letras iniciadas</span>
            <strong>
              {perfil.progreso.letras_iniciadas}
            </strong>
          </div>

          <div>
            <span>Letras dominadas</span>
            <strong>
              {perfil.progreso.letras_dominadas}
            </strong>
          </div>

          <div>
            <span>Letras pendientes</span>
            <strong>
              {letrasPendientes}
            </strong>
          </div>

          <div>
            <span>Intentos</span>
            <strong>
              {perfil.progreso.cantidad_intentos}
            </strong>
          </div>

          <div>
            <span>Aciertos</span>
            <strong>
              {perfil.progreso.cantidad_aciertos}
            </strong>
          </div>
        </div>

        {perfil.progreso.letras_iniciadas === 0 && (
          <p className="perfilSinProgreso">
            Aún no tienes progreso registrado. Comienza una práctica
            para avanzar.
          </p>
        )}
      </section>
    </div>
  );
}

export default Perfil;