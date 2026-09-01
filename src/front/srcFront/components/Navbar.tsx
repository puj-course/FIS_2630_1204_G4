import { FaGraduationCap, FaTools, FaTrophy, FaUser, FaQuestionCircle, FaSignOutAlt } from "react-icons/fa";

interface Props {
  cambiarPagina: (pagina: string) => void;
  paginaActual:string;
  cerrarSesion: () => void;
}

function Navbar({ cambiarPagina, paginaActual,cerrarSesion }: Props) {

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
      <div className="inferior">
        <div className="fraseinf"> 
            Aprender para comunicar,
          <br/>
          comunicar para incluir
        </div>
        <button className="botonMenu">
          <FaQuestionCircle />
          Ayuda
        </button>
        <button className="botonMenu" onClick={cerrarSesion}>
          <FaSignOutAlt />
          Cerrar sesión
        </button>

      </div>

    </nav>
  );
}

export default Navbar;