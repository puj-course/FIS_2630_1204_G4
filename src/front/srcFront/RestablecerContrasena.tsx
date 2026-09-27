import { useState, type FormEvent } from "react";
import { ErrorApi } from "./services/api";
import { restablecerContrasena } from "./services/recuperacion";

interface Props {
  cambiarPagina: (pagina: string) => void;
}

function RestablecerContrasena({ cambiarPagina }: Props) {
  const [token] = useState(
    () => new URLSearchParams(window.location.hash.slice(1)).get("token") ?? ""
  );
  const [nuevaContrasena, setNuevaContrasena] = useState("");
  const [confirmacion, setConfirmacion] = useState("");
  const [cargando, setCargando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");
  const [mensajeExito, setMensajeExito] = useState("");

  const tokenValido = /^[A-Za-z0-9_-]{43}$/.test(token);

  function volverAlLogin() {
    window.history.replaceState(null, "", "/");
    cambiarPagina("login");
  }

  async function manejarRestablecimiento(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    setMensajeError("");

    if (!tokenValido) {
      setMensajeError("El enlace de recuperación no es válido. Solicita uno nuevo.");
      return;
    }

    if (nuevaContrasena.length < 12 || nuevaContrasena.length > 200) {
      setMensajeError("La contraseña debe tener entre 12 y 200 caracteres.");
      return;
    }

    if (nuevaContrasena !== confirmacion) {
      setMensajeError("Las contraseñas no coinciden.");
      return;
    }

    setCargando(true);

    try {
      const respuesta = await restablecerContrasena({
        token,
        nueva_contrasena: nuevaContrasena,
        confirmacion_contrasena: confirmacion
      });

      setMensajeExito(respuesta.mensaje);
      setNuevaContrasena("");
      setConfirmacion("");
      window.history.replaceState(null, "", "/");
    } catch (error) {
      setMensajeError(
        error instanceof ErrorApi
          ? error.message
          : "No fue posible actualizar la contraseña."
      );
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="pantalla recuperarPantalla">
      <h1 className="logo">SignIA</h1>
      <h2>Restablecer contraseña</h2>

      {mensajeExito ? (
        <p role="status">{mensajeExito}</p>
      ) : !tokenValido ? (
        <p role="alert">
          El enlace de recuperación no es válido. Solicita uno nuevo.
        </p>
      ) : (
        <>
          <p>Ingresa y confirma tu nueva contraseña.</p>

          <form onSubmit={manejarRestablecimiento}>
            <input
              type="password"
              placeholder="Nueva contraseña"
              aria-label="Nueva contraseña"
              autoComplete="new-password"
              value={nuevaContrasena}
              onChange={(evento) => setNuevaContrasena(evento.target.value)}
              disabled={cargando}
              required
            />

            <input
              type="password"
              placeholder="Confirmar nueva contraseña"
              aria-label="Confirmar nueva contraseña"
              autoComplete="new-password"
              value={confirmacion}
              onChange={(evento) => setConfirmacion(evento.target.value)}
              disabled={cargando}
              required
            />

            {mensajeError && <p role="alert">{mensajeError}</p>}

            <button type="submit" disabled={cargando}>
              {cargando ? "Actualizando..." : "Cambiar contraseña"}
            </button>
          </form>
        </>
      )}

      <button type="button" onClick={volverAlLogin}>
        Volver al inicio de sesión
      </button>
    </div>
  );
}

export default RestablecerContrasena;