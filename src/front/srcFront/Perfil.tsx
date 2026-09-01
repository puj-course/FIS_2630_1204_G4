interface Props {

  usuario:{
    nombre:string;
    correo:string;
  }

}

function Perfil({ usuario }: Props){

  return(
    <div className="perfil">
      <section className="perfilHeader">

        <div className="usuario">
          <div className="avatar">
            👷
          </div>
          <div>
            <h2>
              Juan Pablo
            </h2>

            <p>
              Nivel Basico - LSC
            </p>
          </div>
          </div>
          <div className="estadisticas">
            <div className="estadistica">
              📈
              <div>
                <small>
                  Racha Actual
                </small>

                <strong>
                  14 dias
                </strong>
              </div>

            </div>
            <div className="estadistica">
              <div>
                <small>
                  Horas Totales
                </small>
                
                <strong>
                  5 horas
                </strong>
              </div>
            </div>
          </div>
      </section> 

      <section className="progreso">
        <h2>
          Progreso Aprendizaje
        </h2>

        <div className="modulos">

          <div className="modulo">
            📌
            <p>
              Modulo 1: Saludos basicos
            </p>

            <span>
              Completado
            </span>

            <div className="barra">
              <div></div>
            </div>
          </div>
            <div className="modulo">
              👥
              <p>
                Modulo 2: Familia y amigos
              </p>

              <span>
                En progreso
              </span>

              <div className="barra">
                <div></div>
              </div>
            </div>

            <div className="modulo">
              🥚
              <p>
                Modulo 3: Comida
              </p>
              <span>
                🔒
              </span>
              <div className="barra">
                <div></div>
              </div>

            </div>
          </div>
      </section>  

      <section className="historial">
        <h2>
          Historial reciente
        </h2>
        <p>
          Practica de camara
        </p>
        <p>
          Logo desbloqueado
        </p>
        <p>
          Cuestionario completado
        </p>
      </section>

      <section className="continuar">
        <h3>
          Continuar aprendiendo
        </h3>
        <p>
          Revision de gestos de cortesia (90% precision)
        </p>
        <button>
          Retomar Sesion --
        </button>

      </section>
    </div>
  )

}

export default Perfil;