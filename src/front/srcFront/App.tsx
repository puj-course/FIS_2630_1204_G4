import { useState } from "react";

import { eliminarSesion, obtenerSesion } from "./services/autenticacion";

import Navbar from "./components/Navbar";
import EstadoBackend from "./components/EstadoBackend";
import Ayuda from "./components/Ayuda";
import AdminUsuarios from "./AdminUsuarios";

import Login from "./Login";
import Registro from "./Registro";
import Perfil from "./Perfil";
import Practica from "./Practica";
import Home from "./Home";
import Aprender from "./Aprender";
import Recuperar from "./Recuperar";
import RestablecerContrasena from "./RestablecerContrasena";

function App() {
  const [logueado, setLogueado] = useState(false);
  const [pagina, setPagina] = useState(
    () => window.location.pathname === "/restablecer-contrasena"
      ? "restablecer-contrasena"
      : "login"
  );
  const [mostrarAyuda, setMostrarAyuda] = useState(false);

  const [idLetraPractica, setIdLetraPractica] =
    useState<number | null>(null);

  const [, setUsuario] = useState({
    nombre: "",
    correo: ""
  });

  const esAdministrador =
  obtenerSesion()?.usuario.rol === "administrador";

  const cambiarPaginaGeneral = (
    nuevaPagina: string
  ) => {
    if (nuevaPagina === "practica") {
      setIdLetraPractica(null);
    }

    setPagina(nuevaPagina);
  };

  const cambiarPaginaDesdeAprender = (
    nuevaPagina: string,
    idLetra?: number
  ) => {
    if (nuevaPagina === "practica") {
      setIdLetraPractica(idLetra ?? null);
    }

    setPagina(nuevaPagina);
  };

  return (
    <>
      <EstadoBackend />

      {!logueado ? (
        pagina === "restablecer-contrasena" ? (
          <RestablecerContrasena
            cambiarPagina={setPagina}
          />
        ) : pagina === "registro" ? (
          <Registro
            cambiarPagina={setPagina}
            guardarUsuario={setUsuario}
          />
        ) : pagina === "recuperar" ? (
          <Recuperar
            cambiarPagina={setPagina}
          />
        ) : (
          <Login
            cambiarPagina={setPagina}
            alIniciarSesion={() => {
              setLogueado(true);
              setPagina("home");
            }}
          />
        )
      ) : (
        <div className="app">
          <Navbar
            cambiarPagina={cambiarPaginaGeneral}
            paginaActual={pagina}
            cerrarSesion={() => {
              eliminarSesion();
              setLogueado(false);
              setPagina("login");
              setIdLetraPractica(null);

              setUsuario({
                nombre: "",
                correo: ""
              });
            }}
            abrirAyuda={() =>
              setMostrarAyuda(true)
            }
            esAdministrador={esAdministrador}
          />

          {mostrarAyuda && (
            <Ayuda
              onCerrar={() =>
                setMostrarAyuda(false)
              }
            />
          )}

          <main>
            {pagina === "home" ? (
              <Home
                cambiarPagina={cambiarPaginaGeneral}
              />
            ) : pagina === "aprender" ? (
              <Aprender
                cambiarPagina={
                  cambiarPaginaDesdeAprender
                }
              />
            ) : pagina === "perfil" ? (
              <Perfil />
             ) : pagina === "admin" && esAdministrador ? (
              <AdminUsuarios />
            ) : (
              <Practica
                key={
                  idLetraPractica
                  ?? "sin-letra"
                }
                idLetraPractica={
                  idLetraPractica
                }
                cambiarPagina={
                  cambiarPaginaGeneral
                }
              />
            )}
          </main>
        </div>
      )}
    </>
  );
}

export default App;