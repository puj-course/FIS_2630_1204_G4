import { useState } from "react";

import Navbar from "./components/Navbar";
import EstadoBackend from "./components/EstadoBackend";
import Login from "./Login";
import Registro from "./Registro";
import Perfil from "./Perfil";
import Practica from "./Practica";
import Home from "./Home";


function App() {

  const [logueado, setLogueado] = useState(false);

  const [pagina, setPagina] = useState("home");


  return (

    <>

      <EstadoBackend />


      {!logueado ? (

        pagina === "registro" ?

        <Registro cambiarPagina={setPagina} />

        :

        <Login 
        cambiarPagina={(pagina) => {

          if(pagina === "home"){

            setLogueado(true);
            setPagina("home");

          }else{

            setPagina(pagina);

          }

        }}
      />


      ) : (


        <div className="app">

          <Navbar
            cambiarPagina={setPagina}
            paginaActual={pagina}
          />


         <main>
          {
            pagina === "home" ? <Home cambiarPagina={setPagina}/> : pagina === "perfil" ? <Perfil /> : <Practica />
          }
          </main>


        </div>


      )}

    </>

  );

}


export default App;