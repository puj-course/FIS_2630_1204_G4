import "./AdminUsuarios.css";
import { useState, useEffect } from "react";

import { obtenerSesion } from "./services/autenticacion";
import {
  obtenerUsuarios,
  cambiarRolUsuario,
  desactivarUsuario,
  type UsuarioListado
} from "./services/usuariosAdmin";
import { ErrorApi } from "./services/api";

function formatearFecha(fechaIso: string): string {
  return new Date(fechaIso).toLocaleDateString("es-CO", {
    year: "numeric",
    month: "short",
    day: "numeric"
  });
}

function AdminUsuarios() {
  const [busqueda, setBusqueda] = useState("");
  const [usuarios, setUsuarios] = useState<UsuarioListado[]>([]);
  const [cargando, setCargando] = useState(true);
  const [errorCarga, setErrorCarga] = useState("");

  const [usuarioAConfirmar, setUsuarioAConfirmar] =
    useState<UsuarioListado | null>(null);

  const [procesandoAccion, setProcesandoAccion] = useState(false);

  const [mensajeAccion, setMensajeAccion] = useState<{
    tipo: "exito" | "error";
    texto: string;
  } | null>(null);

  const sesion = obtenerSesion();

  useEffect(() => {
    let activo = true;

    const idTimeout = setTimeout(() => {
      const cargarUsuarios = async () => {
        if (!sesion) {
          if (activo) {
            setCargando(false);
          }
          return;
        }

        if (activo) {
          setCargando(true);
        }

        try {
          const resultado = await obtenerUsuarios(
            busqueda,
            sesion.access_token
          );

          if (activo) {
            setUsuarios(resultado);
            setErrorCarga("");
          }
        } catch (error) {
          if (activo) {
            setErrorCarga(
              error instanceof ErrorApi
                ? error.message
                : "No fue posible cargar la lista de usuarios"
            );
          }
        } finally {
          if (activo) {
            setCargando(false);
          }
        }
      };

      void cargarUsuarios();
    }, 400);

    return () => {
      activo = false;
      clearTimeout(idTimeout);
    };
  }, [busqueda, sesion?.access_token]);

  async function manejarCambioRol(
    usuario: UsuarioListado,
    nuevoRol: "usuario" | "administrador"
  ) {
    if (!sesion) return;

    setProcesandoAccion(true);
    setMensajeAccion(null);

    try {
      const actualizado = await cambiarRolUsuario(
        usuario.id_usuario,
        nuevoRol,
        sesion.access_token
      );

      setUsuarios((previos) =>
        previos.map((u) =>
          u.id_usuario === actualizado.id_usuario ? actualizado : u
        )
      );

      setMensajeAccion({
        tipo: "exito",
        texto: `Rol de ${actualizado.nombre} actualizado a ${actualizado.rol}`
      });
    } catch (error) {
      setMensajeAccion({
        tipo: "error",
        texto:
          error instanceof ErrorApi
            ? error.message
            : "No fue posible cambiar el rol del usuario"
      });
    } finally {
      setProcesandoAccion(false);
    }
  }

  async function confirmarDesactivacion() {
    if (!sesion || !usuarioAConfirmar) return;

    setProcesandoAccion(true);
    setMensajeAccion(null);

    try {
      await desactivarUsuario(
        usuarioAConfirmar.id_usuario,
        sesion.access_token
      );

      setUsuarios((previos) =>
        previos.filter(
          (u) => u.id_usuario !== usuarioAConfirmar.id_usuario
        )
      );

      setMensajeAccion({
        tipo: "exito",
        texto: `${usuarioAConfirmar.nombre} fue desactivado correctamente`
      });
    } catch (error) {
      setMensajeAccion({
        tipo: "error",
        texto:
          error instanceof ErrorApi
            ? error.message
            : "No fue posible desactivar al usuario"
      });
    } finally {
      setProcesandoAccion(false);
      setUsuarioAConfirmar(null);
    }
  }

  return (
    <div className="adminUsuarios">
      <h1>Administrar usuarios</h1>
      <p>Consulta los usuarios registrados en SignIA.</p>

      <input
        className="buscadorUsuarios"
        type="text"
        placeholder="Buscar por nombre o correo..."
        value={busqueda}
        onChange={(evento) => setBusqueda(evento.target.value)}
      />

      {cargando && (
        <p role="status">Cargando usuarios...</p>
      )}

      {!cargando && errorCarga && (
        <div className="mensajeError" role="alert">
          <p>{errorCarga}</p>
        </div>
      )}

      {!cargando && !errorCarga && usuarios.length === 0 && (
        <div className="mensajeSinUsuarios" role="status">
          <p>No se encontraron usuarios para esta búsqueda.</p>
        </div>
      )}

      {mensajeAccion && (
        <div
          className={
            mensajeAccion.tipo === "exito"
              ? "mensajeExitoAdmin"
              : "mensajeErrorAdmin"
          }
          role={mensajeAccion.tipo === "error" ? "alert" : "status"}
        >
          <p>{mensajeAccion.texto}</p>
        </div>
      )}

      {!cargando && !errorCarga && usuarios.length > 0 && (
        <table className="tablaUsuarios">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Registrado</th>
              <th>Acciones</th>
            </tr>
          </thead>

          <tbody>
            {usuarios.map((usuario) => {
              const esUnoMismo =
                sesion?.usuario.id_usuario === usuario.id_usuario;

              return (
                <tr key={usuario.id_usuario}>
                  <td>{usuario.nombre}</td>
                  <td>{usuario.correo}</td>
                  <td>
                    <select
                      value={usuario.rol}
                      disabled={esUnoMismo || procesandoAccion}
                      onChange={(evento) =>
                        manejarCambioRol(
                          usuario,
                          evento.target.value as "usuario" | "administrador"
                        )
                      }
                    >
                      <option value="usuario">Usuario</option>
                      <option value="administrador">Administrador</option>
                    </select>
                  </td>
                  <td>{formatearFecha(usuario.fecha_creacion)}</td>
                  <td>
                    <button
                      className="botonDesactivarUsuario"
                      disabled={esUnoMismo || procesandoAccion}
                      onClick={() => setUsuarioAConfirmar(usuario)}
                    >
                      Desactivar
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}

      {usuarioAConfirmar && (
        <div className="overlayConfirmacion" role="presentation">
          <div className="modalConfirmacion" role="dialog" aria-modal="true">
            <h2>Confirmar desactivación</h2>

            <p>
              ¿Seguro que deseas desactivar la cuenta de{" "}
              <strong>{usuarioAConfirmar.nombre}</strong>? Esta acción se
              puede revertir más adelante desde la base de datos.
            </p>

            <div className="botonesConfirmacion">
              <button
                onClick={() => setUsuarioAConfirmar(null)}
                disabled={procesandoAccion}
              >
                Cancelar
              </button>

              <button
                className="botonConfirmarDesactivar"
                onClick={confirmarDesactivacion}
                disabled={procesandoAccion}
              >
                {procesandoAccion ? "Desactivando..." : "Sí, desactivar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminUsuarios;