import "./AdminUsuarios.css";
import { useState, useEffect } from "react";

import { obtenerSesion } from "./services/autenticacion";
import { obtenerUsuarios, type UsuarioListado } from "./services/usuariosAdmin";
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
  }, [busqueda, sesion]);

  return (
    <div className=      "adminUsuarios">
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

      {!cargando && !errorCarga && usuarios.length > 0 && (
        <table className="tablaUsuarios">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Registrado</th>
            </tr>
          </thead>

          <tbody>
            {usuarios.map((usuario) => (
              <tr key={usuario.id_usuario}>
                <td>{usuario.nombre}</td>
                <td>{usuario.correo}</td>
                <td>{usuario.rol}</td>
                <td>{formatearFecha(usuario.fecha_creacion)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default AdminUsuarios;