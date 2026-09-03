import {
  useState,
  type FormEvent
} from "react";

import { ErrorApi } from "./services/api";
import { registrarUsuario } from "./services/autenticacion";


interface Props {

  cambiarPagina: (pagina: string) => void;

  guardarUsuario: (usuario:{
    nombre:string;
    correo:string;
  }) => void;

}

interface ErroresFormulario {
  nombre?: string;
  correo?: string;
  contrasena?: string;
  confirmar?: string;
}

const FORMATO_CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


function validarFormulario(
  nombre: string,
  correo: string,
  contrasena: string,
  confirmar: string
): ErroresFormulario {
  const errores: ErroresFormulario = {};
  const nombreLimpio = nombre.trim();
  const correoLimpio = correo.trim();

  if (!nombreLimpio) {
    errores.nombre = "El nombre es obligatorio.";
  } else if (nombreLimpio.length < 2) {
    errores.nombre =
      "El nombre debe tener mínimo 2 caracteres.";
  } else if (nombreLimpio.length > 100) {
    errores.nombre =
      "El nombre no puede superar los 100 caracteres.";
  }

  if (!correoLimpio) {
    errores.correo = "El correo es obligatorio.";
  } else if (correoLimpio.length < 5) {
    errores.correo =
      "El correo debe tener mínimo 5 caracteres.";
  } else if (correoLimpio.length > 150) {
    errores.correo =
      "El correo no puede superar los 150 caracteres.";
  } else if (!FORMATO_CORREO.test(correoLimpio)) {
    errores.correo =
      "Ingresa un correo electrónico válido.";
  }

  if (!contrasena) {
    errores.contrasena = "La contraseña es obligatoria.";
  } else if (contrasena.length < 12) {
    errores.contrasena =
      "La contraseña debe tener mínimo 12 caracteres.";
  } else if (contrasena.length > 200) {
    errores.contrasena =
      "La contraseña no puede superar los 200 caracteres.";
  }

  if (!confirmar) {
    errores.confirmar =
      "Debes confirmar la contraseña.";
  } else if (contrasena !== confirmar) {
    errores.confirmar =
      "Las contraseñas no coinciden.";
  }

  return errores;
}


function Registro({ cambiarPagina }: Props) {
  const [nombre, setNombre] = useState("");
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [erroresCampos, setErroresCampos] =
    useState<ErroresFormulario>({});
  const [cargando, setCargando] = useState(false);
  const [mensajeError, setMensajeError] = useState("");
  const [mensajeExito, setMensajeExito] = useState("");

  function limpiarErrorCampo(
    campo: keyof ErroresFormulario
  ) {
    setErroresCampos((erroresActuales) => {
      const nuevosErrores = { ...erroresActuales };
      delete nuevosErrores[campo];
      return nuevosErrores;
    });

    setMensajeError("");
  }

  async function manejarRegistro(
    evento: FormEvent<HTMLFormElement>
  ) {
    evento.preventDefault();
    setMensajeError("");

    const errores = validarFormulario(
      nombre,
      correo,
      contrasena,
      confirmar
    );

    if (Object.keys(errores).length > 0) {
      setErroresCampos(errores);
      return;

    }

    setErroresCampos({});
    setCargando(true);

    try {
      const respuesta = await registrarUsuario({
        nombre: nombre.trim(),
        correo: correo.trim().toLowerCase(),
        contrasena
      });

      setMensajeExito(respuesta.mensaje);

    } catch (error) {
      if (error instanceof ErrorApi) {
        if (error.codigoEstado === 422) {
          setMensajeError(
            "El backend rechazó los datos enviados. Revisa el formulario."
          );
        } else {
          setMensajeError(error.message);
        }
      } else {
        setMensajeError(
          "No fue posible completar el registro."
        );
      }

    } finally {
      setCargando(false);
    }
  }

  if (mensajeExito) {
    return (
      <div className="pantalla">
        <h1 className="logo">SignIA</h1>
        <h2>Cuenta creada</h2>

        <p role="status">{mensajeExito}</p>

        <button
          type="button"
          onClick={() => cambiarPagina("login")}
        >
          Ir a iniciar sesión
        </button>
      </div>
    );
  }



  return (

    <div className="pantalla">


      <h1 className="logo">
        SignIA
      </h1>


      <h2>
        Crear cuenta
      </h2>



      <form onSubmit={manejarRegistro} noValidate>
        <input
          type="text"
          placeholder="Nombre completo"
          value={nombre}
          onChange={(evento) => {
            setNombre(evento.target.value);
            limpiarErrorCampo("nombre");
          }}
          aria-invalid={Boolean(erroresCampos.nombre)}
          aria-describedby={
            erroresCampos.nombre ? "error-nombre" : undefined
          }
          autoComplete="name"
          disabled={cargando}
        />

        {erroresCampos.nombre && (
          <p id="error-nombre" role="alert">
            {erroresCampos.nombre}
          </p>
        )}

        <input
          type="email"
          placeholder="Correo electrónico"
          value={correo}
          onChange={(evento) => {
            setCorreo(evento.target.value);
            limpiarErrorCampo("correo");
          }}
          aria-invalid={Boolean(erroresCampos.correo)}
          aria-describedby={
            erroresCampos.correo ? "error-correo" : undefined
          }
          autoComplete="email"
          disabled={cargando}
        />

        {erroresCampos.correo && (
          <p id="error-correo" role="alert">
            {erroresCampos.correo}
          </p>
        )}

        <input
          type="password"
          placeholder="Contraseña"
          value={contrasena}
          onChange={(evento) => {
            setContrasena(evento.target.value);
            limpiarErrorCampo("contrasena");
            limpiarErrorCampo("confirmar");
          }}
          aria-invalid={Boolean(erroresCampos.contrasena)}
          aria-describedby={
            erroresCampos.contrasena
              ? "error-contrasena"
              : undefined
          }
          autoComplete="new-password"
          disabled={cargando}
        />

        {erroresCampos.contrasena && (
          <p id="error-contrasena" role="alert">
            {erroresCampos.contrasena}
          </p>
        )}

        <input
          type="password"
          placeholder="Confirmar contraseña"
          value={confirmar}
          onChange={(evento) => {
            setConfirmar(evento.target.value);
            limpiarErrorCampo("confirmar");
          }}
          aria-invalid={Boolean(erroresCampos.confirmar)}
          aria-describedby={
            erroresCampos.confirmar
              ? "error-confirmar"
              : undefined
          }
          autoComplete="new-password"
          disabled={cargando}
        />

        {erroresCampos.confirmar && (
          <p id="error-confirmar" role="alert">
            {erroresCampos.confirmar}
          </p>
        )}

        {mensajeError && (
          <p role="alert">{mensajeError}</p>
        )}

        <button type="submit" disabled={cargando}>
          {cargando ? "Registrando..." : "Registrarse"}
        </button>
      </form>

      <p>
        ¿Ya tienes cuenta?{" "}
        <span
          className="enlace"
          onClick={() => cambiarPagina("login")}
        >
          Inicia sesión

        </span>


      </p>


    </div>

  );

}


export default Registro;