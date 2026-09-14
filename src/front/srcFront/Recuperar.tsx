import { useState, type FormEvent } from "react";
import { ErrorApi } from "./services/api";
import { solicitarRecuperacion } from "./services/recuperacion";

interface Props {
  cambiarPagina: (pagina: string) => void;
}


function Recuperar({ cambiarPagina }: Props) {

  const [correo, setCorreo] = useState("");
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState("");


  async function manejarRecuperacion(
  evento: FormEvent<HTMLFormElement>
) {

  evento.preventDefault();

  setMensaje("");

  if (!correo.trim()) {
    setMensaje(
      "Debes ingresar un correo electrónico."
    );
    return;
  }


  setCargando(true);


  try {

    const respuesta = await solicitarRecuperacion({
      correo: correo.trim().toLowerCase()
    });


    setMensaje(
      respuesta.mensaje
    );


  } catch(error) {

    setMensaje(
      error instanceof ErrorApi
        ? error.message
        : "No fue posible solicitar la recuperación."
    );


  } finally {

    setCargando(false);

  }

}


  return (
    <div className="pantalla">

      <h1 className="logo">
        SignIA
      </h1>


      <h2>
        Recuperar contraseña
      </h2>


      <p>
        Ingresa tu correo electrónico para recuperar el acceso a tu cuenta.
      </p>


      <form onSubmit={manejarRecuperacion}>


        <input
          type="email"
          placeholder="Correo electrónico"
          value={correo}
          onChange={(evento) =>
            setCorreo(evento.target.value)
          }
          disabled={cargando}
          required
        />


        {mensaje && (
          <p role="alert">
            {mensaje}
          </p>
        )}


        <button
          type="submit"
          disabled={cargando}
        >
          {
            cargando
            ? "Enviando..."
            : "Enviar enlace"
          }
        </button>


      </form>


      <p>
        ¿Recordaste tu contraseña?{" "}

        <span
          className="enlace"
          onClick={() => cambiarPagina("login")}
        >
          Volver al inicio
        </span>

      </p>


    </div>
  );
}


export default Recuperar;