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


  const [pagina, setPagina] = useState("login");



  const [usuario, setUsuario] = useState({

    nombre:"",

    correo:""

  });





  return (

    <>


      <EstadoBackend />



      {!logueado ? (


        pagina === "registro" ?


        <Registro

          cambiarPagina={setPagina}

          guardarUsuario={setUsuario}

        />



        :
        <Login

        cambiarPagina={setPagina}

        alIniciarSesion={()=>{

          setLogueado(true);

          setPagina("home");

        }}

      />



      


      )



      :



      (


        <div className="app">


          <Navbar

            cambiarPagina={setPagina}

            paginaActual={pagina}

            cerrarSesion={()=>{

            setLogueado(false);

            setPagina("login");

            setUsuario({
              nombre:"",
              correo:""
            });

          }}

          />



          <main>


            {

              pagina==="home"

              ?

              <Home cambiarPagina={setPagina}/>



              :



              pagina==="perfil"

              ?


              <Perfil usuario={usuario}/>



              :



              <Practica />


            }


          </main>



        </div>


      )}



    </>

  );


}


export default App;