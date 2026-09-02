import { useState } from "react";

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
        letra:"A", descripcion: "Seña correspondiente a la letra A en Lengua de Señas Colombiana",imagen:""
    },
    {
        letra:"E", descripcion: "Seña correspondiente a la letra B en Lengua de Señas Colombiana",imagen:""
    },
    {
        letra:"I", descripcion: "Seña correspondiente a la letra C en Lengua de Señas Colombiana",imagen:""
    },
    {
        letra:"O", descripcion: "Seña correspondiente a la letra D en Lengua de Señas Colombiana",imagen:""
    },
    {
        letra:"U", descripcion: "Seña correspondiente a la letra E en Lengua de Señas Colombiana",imagen:""
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
                <img src={letraSeleccionada.imagen}/>
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