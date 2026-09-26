import { useState } from "react";

import { eliminarSesion } from "./services/autenticacion";

import Navbar from "./components/Navbar";
import EstadoBackend from "./components/EstadoBackend";
import Ayuda from "./components/Ayuda";

import Login from "./Login";
import Registro from "./Registro";
import Perfil from "./Perfil";
import Practica from "./Practica";
import Home from "./Home";
import Aprender from "./Aprender";
import Recuperar from "./Recuperar";

function App() {
  const [logueado, setLogueado] = useState(false);
  const [pagina, setPagina] = useState("login");
  const [mostrarAyuda, setMostrarAyuda] = useState(false);
  const [idLetraPractica, setIdLetraPractica] =
    useState<number | null>(null);

  const [, setUsuario] = useState({
    nombre: "",
    correo: ""
  });

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
        pagina === "registro" ? (
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
            cambiarPagina={setPagina}
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
            abrirAyuda={() => setMostrarAyuda(true)}
          />

          {mostrarAyuda && (
            <Ayuda
              onCerrar={() => setMostrarAyuda(false)}
            />
          )}

          <main>
            {pagina === "home" ? (
              <Home
                cambiarPagina={setPagina}
              />
            ) : pagina === "aprender" ? (
              <Aprender
                cambiarPagina={cambiarPaginaDesdeAprender}
              />
            ) : pagina === "perfil" ? (
              <Perfil />
            ) : (
              <Practica
                key={idLetraPractica ?? "sin-letra"}
              />
            )}
          </main>
        </div>
      )}
    </>
  );
}

export default App;