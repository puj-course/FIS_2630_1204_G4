import { useState } from "react";
import Navbar from "./components/Navbar";
import Perfil from "./Perfil";
import Practica from "./Practica";


function App() {

  const [pagina, setPagina] = useState("practica");


  return (
    <>
      <Navbar cambiarPagina={setPagina} paginaActual={pagina}/>
      {
        pagina === "perfil"
        ?
        <Perfil />
        :
        <Practica />
      }

    </>
  );
}


export default App;