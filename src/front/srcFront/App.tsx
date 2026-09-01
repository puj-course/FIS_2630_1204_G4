import { useState } from "react";
import Navbar from "./components/Navbar";
import Perfil from "./Perfil";
import Practica from "./Practica";
import Login from "./Login";



function App() {

  const [logueado, setLogueado] = useState(false);
  const [pagina, setPagina] = useState("Practica");

  if(!logueado){
    return(
      <Login cambiarPagina={() => setLogueado(true)}
      />
    );
  }
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