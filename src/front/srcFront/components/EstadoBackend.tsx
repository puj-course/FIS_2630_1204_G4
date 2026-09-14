import { useEffect, useState } from "react";

import { comprobarConexionBackend } from "../services/api";

type EstadoConexion = "comprobando" | "conectado" | "error";

function EstadoBackend() {
  const [estado, setEstado] =
    useState<EstadoConexion>("comprobando");

  const [mensaje, setMensaje] = useState(
    "Verificando conexión con el backend..."
  );

  useEffect(() => {
    let componenteActivo = true;

    comprobarConexionBackend()
      .then((respuesta) => {
        if (!componenteActivo) {
          return;
        }

        setEstado("conectado");
        setMensaje(respuesta.mensaje);
      })
      .catch((error: unknown) => {
        if (!componenteActivo) {
          return;
        }

        setEstado("error");
        setMensaje(
          error instanceof Error
            ? error.message
            : "Ocurrió un error de comunicación."
        );
      });

    return () => {
      componenteActivo = false;
    };
  }, []);

  return (
    <div
      className={`estado-backend estado-backend-${estado}`}
      role={estado === "error" ? "alert" : "status"}
      aria-live="polite"
    >
      {mensaje}
    </div>
  );
}

export default EstadoBackend;