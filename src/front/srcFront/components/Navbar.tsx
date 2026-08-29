import { FaGraduationCap, FaTools, FaTrophy, FaUser } from "react-icons/fa";

interface Props {
  cambiarPagina: (pagina: string) => void;
  paginaActual:string;
}

function Navbar({ cambiarPagina, paginaActual }: Props) {

  return (
    <nav>

      <div className="logoNav">

        <h2>
          SignIA
        </h2>

        <p>
          LSC Learning
        </p>

      </div>


      <div className="Opciones">

        <button 
          className={paginaActual === "aprender" ? "botonActivo" : "botonMenu"}
          onClick={() => cambiarPagina("aprender")}
        >
          <FaGraduationCap />
          Aprender
        </button>


        <button 
          className={paginaActual === "practica" ? "botonActivo" : "botonMenu"}
          onClick={() => cambiarPagina("practica")}
        >
          <FaTools />
          Practicar
        </button>


        <button 
          className={paginaActual === "logros" ? "botonActivo" : "botonMenu"}
          onClick={() => cambiarPagina("logros")}
        >
          <FaTrophy className={paginaActual === "logros" ? "trofeoActivo" : ""}/>
          Logros
        </button>


        <button 
          className={paginaActual === "perfil" ? "botonActivo" : "botonMenu"}
          onClick={() => cambiarPagina("perfil")}
        >
          <FaUser />
          Perfil
        </button>

      </div>

    </nav>
  );
}

export default Navbar;