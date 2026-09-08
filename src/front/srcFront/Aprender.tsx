import { useState } from "react";
import { obtenerSesion } from "./services/autenticacion";

import imagenA from "./assets/señas/LETRA A.jpg";
import imagenB from "./assets/señas/LETRA B.jpg";
import imagenC from "./assets/señas/LETRA C.jpg";
import imagenD from "./assets/señas/LETRA D.jpg";
import imagenE from "./assets/señas/LETRA E.jpg";
import imagenF from "./assets/señas/LETRA F.jpg";
import imagenG from "./assets/señas/LETRA G.jpg";
import imagenH from "./assets/señas/LETRA H.jpg";
import imagenI from "./assets/señas/LETRA I.jpg";
import imagenJ from "./assets/señas/LETRA J.jpg";
import imagenK from "./assets/señas/LETRA K.jpg";
import imagenL from "./assets/señas/LETRA L.jpg";
import imagenM from "./assets/señas/LETRA M.jpg";
import imagenN from "./assets/señas/LETRA N.jpg";
import imagenÑ from "./assets/señas/LETRA Ñ.jpg";
import imagenO from "./assets/señas/LETRA O.jpg";
import imagenP from "./assets/señas/LETRA P.jpg";
import imagenQ from "./assets/señas/LETRA Q.jpg";
import imagenR from "./assets/señas/LETRA R.jpg";
import imagenS from "./assets/señas/LETRA S.jpg";
import imagenT from "./assets/señas/LETRA T.jpg";
import imagenU from "./assets/señas/LETRA U.jpg";
import imagenV from "./assets/señas/LETRA V.jpg";
import imagenW from "./assets/señas/LETRA W.jpg";
import imagenX from "./assets/señas/LETRA X.jpg";
import imagenY from "./assets/señas/LETRA Y.jpg";
import imagenZ from "./assets/señas/LETRA Z.jpg";

const impagePorLetra: Record<string, string> = {
  A: imagenA, B: imagenB, C: imagenC, D: imagenD, E: imagenE, F: imagenF, G: imagenG, H: imagenH,
  I: imagenI, J: imagenJ, K: imagenK, L: imagenL, M: imagenM, N: imagenN, Ñ: imagenÑ, O: imagenO,
  P: imagenP, Q: imagenQ, R: imagenR, S: imagenS, T: imagenT, U: imagenU, V: imagenV, W: imagenW, 
  X: imagenX, Y: imagenY, Z: imagenZ,
}

interface Props{
    cambiarPagina: (pagina:string)=>void;
}

function Aprender({cambiarPagina}:Props){
    const [letraSeleccionada,setLetraSeleccionada] = useState<Letra | null > (null);
    
    const sesion = obtenerSesion();
    const esAdministrador = sesion?.usuario.rol === "administrador";

    const [editando, setEditando] = useState(false);
    const [descripcionEditada, setDescripcionEditada] = useState("");

    const iniciarEdicion = () => {
        if (!letraSeleccionada) return;
        setDescripcionEditada(letraSeleccionada.descripcion);
        setEditando(true);
    };

    const guardarCambios = () => {
        if (!letraSeleccionada) return;
        letraSeleccionada.descripcion = descripcionEditada;
        setEditando(false);
    };

    return(
        <div className="aprender">
            <h1>
                Aprender LSC
            </h1>
            <p>
                Selecciona una letra para conocer su presentacion en lengua de señas
            </p>

            <div className="contenedorLetras">


        {
          letras.map((letra)=>(

            <button

              key={letra.letra}

              className={
                letraSeleccionada?.letra === letra.letra
                ?
                "letraActiva"
                :
                "letraBox"
              }

              onClick={()=>{
                setLetraSeleccionada(letra);
                setEditando(false);
              }}

            >

              {letra.letra}


            </button>


          ))

        }


      </div>



      {
        letraSeleccionada && (


          <section className="detalleLetra">


            <h2>
              Letra {letraSeleccionada.letra}
            </h2>



            <div className="imagenSena">

              {/* img*/}

              {
                letraSeleccionada.imagen
                ?
                <img
                  src={letraSeleccionada.imagen}
                  alt={`Seña letra ${letraSeleccionada.letra}`}
                />
                :
                <p>
                  Imagen de la seña
                </p>

              }


            </div>
     
            {
              !editando && (
                <p>
                  {letraSeleccionada.descripcion}
                </p>
              )
            }

            {
              esAdministrador && editando && (
                <div className="editorDescripcion">
                  <textarea
                    value={descripcionEditada}
                    onChange={(e)=>setDescripcionEditada(e.target.value)}
                    rows={4}
                  />
                  <div className="accionesEdicion">
                    <button onClick={guardarCambios}>
                      Guardar cambios
                    </button>
                    <button
                      className="botonCancelar"
                      onClick={()=>setEditando(false)}
                    >
                      Cancelar
                    </button>
                  </div>
                </div>
              )
            }



            <div className="accionesLetra">


            <button

              className="botonPracticar"

              onClick={()=>cambiarPagina("practica")}

            >

              Practicar esta letra

            </button>
            
            {
                esAdministrador && !editando && (
                  <button className="botonEditar" onClick={iniciarEdicion}>
                    Editar instrucciones
                  </button>
                )
              }

            </div>

          </section>


        )

      }

    </div>

  );


}
export default Aprender;

