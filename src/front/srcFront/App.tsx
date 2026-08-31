import { useState } from "react";
import Navbar from "./components/Navbar";
import Perfil from "./Perfil";
import Practica from "./Practica";


function App() {

  const [pagina, setPagina] = useState("practica");


  return (
    <div className="app">
      <Navbar cambiarPagina={setPagina} paginaActual={pagina}/>
      <main>
        {
          pagina === "perfil" ? <Perfil />:<Practica />
        }
      </main>
    </div>
  );
}


export default App;