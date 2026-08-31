function Practica(){

  return(
    <div className="practica">

      <section className="practicaHeader">
        <div>
          <h1>
            Alfabeto: Letra A
          </h1>
          <p>
            Posiciona tu mano frente a la camara para practicar.
          </p>
        </div>
        <button>
          Apagar camara
        </button>

      </section>

      <section className="zonaPracti">
        <div className="camara">
          <div className="estadoCamara">
            Grabando
          </div>
          <div className="deteccion"> 
            Detectando mano...
          </div>
        </div>
        <div className="panelPractica">
          <div className="objetivo">
            <h3>
              Objetivo
            </h3>
            <strong>
              A
            </strong>
            <p>
              Precision
            </p>
            <div className="barra">
              <div></div>
            </div>

          </div>
          <div className="instrucciones">
            <h2>
              Instrucciones
            </h2>
            <p>
              1. Cierra la mano formando un puño.
            </p>
            <p>
              2. Manten el pulgar apoyado contra el costado del dedo indice.
            </p>
            <p>
              3. Asegurate de que la palma este orientada hacia la camara.
            </p>

          </div>

        </div>

      </section>

      <section className="alfabeto">
        <h3>
          Navegador alfabeto
        </h3>
        <button className="letraActiva">
          A
        </button>
        <button>
          B
        </button>
        <button>
          C
        </button>
        <button>
          D
        </button>
        <button>
          E
        </button>
        <button>
          F
        </button>

      </section>


    </div>
  )

}

export default Practica;