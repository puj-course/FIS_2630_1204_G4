import {
  useState,
  type FormEvent
} from "react";

import { ErrorApi } from "./services/api";
import { registrarUsuario } from "./services/autenticacion";


interface Props {
  cambiarPagina: (pagina: string) => void;
}


function Registro({ cambiarPagina }: Props) {
  const [nombre, setNombre] = useState("");
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [cargando, setCargando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");
  const [mensajeExito, setMensajeExito] = useState("");

  async function manejarRegistro(
    evento: FormEvent<HTMLFormElement>
  ) {
    evento.preventDefault();
    setMensajeError("");

    if (contrasena !== confirmar) {
      setMensajeError("Las contraseñas no coinciden.");
      return;
    }

    setCargando(true);

    try {
      const respuesta = await registrarUsuario({
        nombre: nombre.trim(),
        correo: correo.trim().toLowerCase(),
        contrasena
      });

      setMensajeExito(respuesta.mensaje);

    } catch (error) {
      if (error instanceof ErrorApi) {
        if (error.codigoEstado === 422) {
          setMensajeError(
            "Revisa que todos los datos sean válidos."
          );
        } else {
          setMensajeError(error.message);
        }
      } else {
        setMensajeError(
          "No fue posible completar el registro."
        );
      }

    } finally {
      setCargando(false);
    }
  }

  if (mensajeExito) {
    return (
      <div className="pantalla">
        <h1 className="logo">SignIA</h1>
        <h2>Cuenta creada</h2>

        <p role="status">{mensajeExito}</p>

        <button
          type="button"
          onClick={() => cambiarPagina("login")}
        >
          Ir a iniciar sesión
        </button>
      </div>
    );
  }

  return (
    <div className="pantalla">
      <h1 className="logo">SignIA</h1>
      <h2>Crear cuenta</h2>

      <form onSubmit={manejarRegistro}>
        <input
          type="text"
          placeholder="Nombre completo"
          value={nombre}
          onChange={(evento) => setNombre(evento.target.value)}
          minLength={2}
          maxLength={100}
          autoComplete="name"
          disabled={cargando}
          required
        />

        <input
          type="email"
          placeholder="Correo electrónico"
          value={correo}
          onChange={(evento) => setCorreo(evento.target.value)}
          minLength={5}
          maxLength={150}
          autoComplete="email"
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
          minLength={12}
          maxLength={200}
          autoComplete="new-password"
          disabled={cargando}
          required
        />

        <input
          type="password"
          placeholder="Confirmar contraseña"
          value={confirmar}
          onChange={(evento) =>
            setConfirmar(evento.target.value)
          }
          minLength={12}
          maxLength={200}
          autoComplete="new-password"
          disabled={cargando}
          required
        />

        {mensajeError && (
          <p role="alert">{mensajeError}</p>
        )}

        <button type="submit" disabled={cargando}>
          {cargando ? "Registrando..." : "Registrarse"}
        </button>
      </form>

      <p>
        ¿Ya tienes cuenta?{" "}
        <span
          className="enlace"
          onClick={() => cambiarPagina("login")}
        >
          Inicia sesión
        </span>
      </p>
    </div>
  );
}

export default Registro;