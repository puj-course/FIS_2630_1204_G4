import { useState } from "react";

import imagenA from "./assets/señas/LETRA A.jpg";
import imagenE from "./assets/señas/LETRA E.jpg";
import imagenI from "./assets/señas/LETRA I.jpg";
import imagenO from "./assets/señas/LETRA O.jpg";
import imagenU from "./assets/señas/LETRA U.jpg";

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
        letra:"A", descripcion: "La letra A en Lenguaje de Señas Colombiana se realiza formando un puño con los dedos cerrados sobre la palma de la mano. El pulgar debe estar apoyado al costado del dedo indice, creando la configuracion caracteristica de esta letra.",imagen:imagenA
    },
    {
        letra:"E", descripcion: "La letra E en Lengua de Senas Colombiana se realiza manteniendo los dedos flexionados hacia la palma de la mano, con el pulgar ubicado sobre ellos. Esta configuracion representa la segunda vocal del alfabeto.",imagen:imagenE
    },
    {
        letra:"I", descripcion: "La letra I en Lengua de Senas Colombiana se representa manteniendo los dedos cerrados sobre la palma de la mano y extendiendo unicamente el dedo meñique hacia arriba. Esta configuracion corresponde a la tercera vocal del alfabeto.",imagen:imagenI
    },
    {
        letra:"O", descripcion: "La letra O en Lengua de Senas Colombiana se realiza uniendo las puntas de los dedos con el pulgar formando una figura circular. Esta configuracion representa la forma de la letra O dentro del alfabeto.",imagen:imagenO
    },
    {
        letra:"U", descripcion: "La letra U en Lengua de Senas Colombiana se representa manteniendo los dedos indice y medio extendidos y juntos, mientras los demas dedos permanecen cerrados. Esta configuracion corresponde a la ultima vocal del alfabeto.",imagen:imagenU
    },

];

function Aprender({cambiarPagina}:Props){
    const [letraSeleccionada,setLetraSeleccionada] = useState<Letra | null > (null);
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

              onClick={()=>setLetraSeleccionada(letra)}

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



            <p>

              {letraSeleccionada.descripcion}

            </p>



            <button

              className="botonPracticar"

              onClick={()=>cambiarPagina("practica")}

            >

              Practicar esta letra

            </button>


          </section>


        )

      }



    </div>

  );


}


export default Aprender;