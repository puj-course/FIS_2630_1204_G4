import {
  useState,
  type FormEvent
} from "react";

import { ErrorApi } from "./services/api";
import {
  guardarSesion,
  iniciarSesion,
  type RespuestaLogin
} from "./services/autenticacion";


interface Props {
  cambiarPagina: (pagina: string) => void;
  alIniciarSesion: (sesion: RespuestaLogin) => void;
}


function Login({
  cambiarPagina,
  alIniciarSesion
}: Props) {
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [cargando, setCargando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");

  async function manejarLogin(
    evento: FormEvent<HTMLFormElement>
  ) {
    evento.preventDefault();
    setMensajeError("");

    if (!correo.trim() || !contrasena) {
      setMensajeError(
        "Debes ingresar el correo y la contraseña."
      );
      return;
    }

    setCargando(true);

    try {
      const sesion = await iniciarSesion({
        correo: correo.trim().toLowerCase(),
        contrasena
      });

      guardarSesion(sesion);
      alIniciarSesion(sesion);

    } catch (error) {
      setMensajeError(
        error instanceof ErrorApi
          ? error.message
          : "No fue posible iniciar sesión."
      );

    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="pantalla">
      <h1 className="logo">SignIA</h1>
      <h2>Iniciar sesión</h2>

      <form onSubmit={manejarLogin}>
        <input
          type="email"
          placeholder="Correo electrónico"
          value={correo}
          onChange={(evento) => setCorreo(evento.target.value)}
          disabled={cargando}
          required
        />

        <input
          type="password"
          placeholder="Contraseña"
          value={contrasena}
          onChange={(evento) =>
            setContrasena(evento.target.value)
          }
          disabled={cargando}
          required
        />

        {mensajeError && (
          <p role="alert">{mensajeError}</p>
        )}

        <button type="submit" disabled={cargando}>
          {cargando ? "Validando..." : "Iniciar sesión"}
        </button>
      </form>

      <p>
        ¿No tienes cuenta?{" "}
        <span
          className="enlace"
          onClick={() => cambiarPagina("registro")}
        >
          Regístrate
        </span>
      </p>
    </div>
  );
}

export default Login;