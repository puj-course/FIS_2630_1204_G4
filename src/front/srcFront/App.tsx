import { useState } from "react";

import Navbar from "./components/Navbar";
import EstadoBackend from "./components/EstadoBackend";
import Login from "./Login";
import Perfil from "./Perfil";
import Practica from "./Practica";

function App() {
  const [logueado, setLogueado] = useState(false);
  const [pagina, setPagina] = useState("Practica");

  return (
    <>
      <EstadoBackend />

      {!logueado ? (
        <Login cambiarPagina={() => setLogueado(true)} />
      ) : (
        <div className="app">
          <Navbar
            cambiarPagina={setPagina}
            paginaActual={pagina}
          />

          <main>
            {pagina === "perfil" ? <Perfil /> : <Practica />}
          </main>
        </div>
      )}
    </>
  );
}

export default App;