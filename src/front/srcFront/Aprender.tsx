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

interface Props{
    cambiarPagina: (pagina:string)=>void;
}
interface Letra{
    letra:string;
    descripcion: string;
    imagen: string;
}

const letras:Letra[] = [
    {
        letra:"A", descripcion: "La letra A en Lengua de Señas Colombiana se realiza formando un puño con los dedos cerrados sobre la palma de la mano. El pulgar debe estar apoyado al costado del dedo índice, creando la configuración característica de esta letra.",imagen:imagenA
    },
    {
        letra:"B", descripcion: "La letra B en Lengua de Señas Colombiana se realiza con la mano abierta, los cuatro dedos extendidos y juntos hacia arriba, mientras el pulgar se dobla sobre la palma de la mano.",imagen:imagenB
    },
    {
        letra:"C", descripcion: "La letra C en Lengua de Señas Colombiana se representa curvando los dedos y el pulgar para formar la silueta de la letra C, dejando un espacio abierto entre ellos como si se sostuviera un objeto circular.",imagen:imagenC
    },
    {
        letra:"D", descripcion: "La letra D en Lengua de Señas Colombiana se realiza extendiendo el dedo índice hacia arriba mientras el pulgar y los demás dedos se unen formando un círculo en la base.",imagen:imagenD
    },
    {
        letra:"E", descripcion: "La letra E en Lengua de Señas Colombiana se realiza manteniendo los dedos flexionados hacia la palma de la mano, con el pulgar ubicado sobre ellos. Esta configuración representa la segunda vocal del alfabeto.",imagen:imagenE
    },
    {
        letra:"F", descripcion: "La letra F en Lengua de Señas Colombiana se representa uniendo las puntas del pulgar y el índice en un pequeño círculo, mientras los dedos medio, anular y meñique permanecen extendidos.",imagen:imagenF
    },
    {
        letra:"G", descripcion: "La letra G en Lengua de Señas Colombiana se realiza extendiendo el dedo índice y el pulgar de forma paralela y horizontal, manteniendo una pequeña separación entre ambos.",imagen:imagenG
    },
    {
        letra:"H", descripcion: "La letra H en Lengua de Señas Colombiana se representa extendiendo los dedos índice y medio juntos en posición horizontal, mientras el pulgar y los demás dedos permanecen cerrados.",imagen:imagenH
    },
    {
        letra:"I", descripcion: "La letra I en Lengua de Senas Colombiana se representa manteniendo los dedos cerrados sobre la palma de la mano y extendiendo unicamente el dedo meñique hacia arriba. Esta configuracion corresponde a la tercera vocal del alfabeto.",imagen:imagenI
    },
    {
        letra:"J", descripcion: "La letra J en Lengua de Señas Colombiana parte de la configuración de la letra I, con el dedo meñique extendido, y se traza en el aire una trayectoria curva que representa el trazo de esta letra.",imagen:imagenJ
    },
    {
        letra:"K", descripcion: "La letra K en Lengua de Señas Colombiana se realiza extendiendo los dedos índice y medio en forma de V, mientras el pulgar se apoya entre ambos dedos, tocando la base del dedo medio.",imagen:imagenK
    },
    {
        letra:"L", descripcion: "La letra L en Lengua de Señas Colombiana se representa extendiendo el dedo índice hacia arriba y el pulgar hacia el costado, formando un ángulo recto que asemeja la forma de la letra.",imagen:imagenL
    },
    {
        letra:"M", descripcion: "La letra M en Lengua de Señas Colombiana se realiza colocando el pulgar debajo de los dedos índice, medio y anular, los cuales se doblan hacia la palma cubriéndolo.",imagen:imagenM
    },
    {
        letra:"N", descripcion: "La letra N en Lengua de Señas Colombiana se realiza colocando el pulgar debajo de los dedos índice y medio, los cuales se doblan hacia la palma cubriéndolo.",imagen:imagenN
    },
    {
        letra:"Ñ", descripcion: "La letra Ñ en Lengua de Señas Colombiana parte de la configuración de la letra N, agregando un movimiento ondulante con la mano que representa la virgulilla característica de esta letra propia del español.",imagen:imagenÑ
    },
    {
        letra:"O", descripcion: "La letra O en Lengua de Senas Colombiana se realiza uniendo las puntas de los dedos con el pulgar formando una figura circular. Esta configuracion representa la forma de la letra O dentro del alfabeto.",imagen:imagenO
    },
    {
        letra:"P", descripcion: "La letra P en Lengua de Señas Colombiana se realiza con la misma configuración de la letra K, pero orientando la mano hacia abajo en lugar de hacia arriba.",imagen:imagenP
    },
    {
        letra:"Q", descripcion: "La letra Q en Lengua de Señas Colombiana se representa con la misma configuración de la letra G, pero orientando la mano hacia abajo en lugar de en posición horizontal hacia el frente.",imagen:imagenQ
    },
    {
        letra:"R", descripcion: "La letra R en Lengua de Señas Colombiana se realiza cruzando el dedo índice sobre el dedo medio, mientras los demás dedos permanecen cerrados.",imagen:imagenR
    },
    {
        letra:"S", descripcion: "La letra S en Lengua de Señas Colombiana se realiza formando un puño cerrado con el pulgar colocado sobre los demás dedos por delante.",imagen:imagenS
    },
    {
        letra:"T", descripcion: "La letra T en Lengua de Señas Colombiana se representa formando un puño cerrado con el pulgar ubicado entre el dedo índice y el dedo medio.",imagen:imagenT
    },
    {
        letra:"U", descripcion: "La letra U en Lengua de Senas Colombiana se representa manteniendo los dedos indice y medio extendidos y juntos, mientras los demas dedos permanecen cerrados. Esta configuracion corresponde a la ultima vocal del alfabeto.",imagen:imagenU
    },
    {
        letra:"V", descripcion: "La letra V en Lengua de Señas Colombiana se realiza extendiendo los dedos índice y medio separados formando una V, mientras el pulgar y los demás dedos permanecen cerrados.",imagen:imagenV
    },
    {
        letra:"W", descripcion: "La letra W en Lengua de Señas Colombiana se representa extendiendo los dedos índice, medio y anular separados entre sí, mientras el pulgar sostiene el meñique doblado.",imagen:imagenW
    },
    {
        letra:"X", descripcion: "La letra X en Lengua de Señas Colombiana se realiza doblando el dedo índice en forma de gancho, mientras los demás dedos permanecen cerrados en el puño.",imagen:imagenX
    },
    {
        letra:"Y", descripcion: "La letra Y en Lengua de Señas Colombiana se realiza extendiendo el pulgar y el dedo meñique, mientras los dedos índice, medio y anular permanecen doblados hacia la palma.",imagen:imagenY
    },
    {
        letra:"Z", descripcion: "La letra Z en Lengua de Señas Colombiana se representa extendiendo el dedo índice y trazando en el aire la forma de la letra Z, con los demás dedos cerrados.",imagen:imagenZ
    },
];

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

