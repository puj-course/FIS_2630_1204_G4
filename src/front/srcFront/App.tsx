import { useState } from "react";

import Navbar from "./components/Navbar";
import EstadoBackend from "./components/EstadoBackend";
import Login from "./Login";
import Registro from "./Registro";
import Perfil from "./Perfil";
import Practica from "./Practica";
import Home from "./Home";
import {
  eliminarSesion,
  obtenerSesion,
  type RespuestaLogin
} from "./services/autenticacion";


function App() {
  const [sesion, setSesion] =
    useState<RespuestaLogin | null>(() => obtenerSesion());

  const [pagina, setPagina] = useState("home");

  function cerrarSesion() {
    eliminarSesion();
    setSesion(null);
    setPagina("login");
  }

  return (
    <>
      <EstadoBackend />

      {!sesion ? (
        pagina === "registro" ? (
          <Registro cambiarPagina={setPagina} />
        ) : (
          <Login
            cambiarPagina={setPagina}
            alIniciarSesion={(nuevaSesion) => {
              setSesion(nuevaSesion);
              setPagina("home");
            }}
          />
        )
      ) : (
        <div className="app">
          <Navbar
            cambiarPagina={setPagina}
            paginaActual={pagina}
            cerrarSesion={cerrarSesion}
          />

          <main>
            {pagina === "home" ? (
              <Home cambiarPagina={setPagina} />
            ) : pagina === "perfil" ? (
              <Perfil />
            ) : (
              <Practica />
            )}
          </main>
        </div>
      )}
    </>
  );
}

export default App;