import {
  useState,
  type RefObject,
} from "react";

import { ErrorApi } from "../services/api";
import { obtenerSesion } from "../services/autenticacion";
import { registrarResultadoReconocimiento } from "../services/resultados";
import { useReconocimiento } from "../hooks/useReconocimiento";


const CONFIANZA_MINIMA = 0.80;


interface Props {
  videoRef: RefObject<HTMLVideoElement | null>;
  idLetraObjetivo: number | null;
}


function ResultadoReconocimiento({
  videoRef,
  idLetraObjetivo,
}: Props) {
  const {
    resultado,
    confianza,
    procesando,
    mensajeError,
    reintentar,
  } = useReconocimiento(videoRef);

  const [guardando, setGuardando] = useState(false);
  const [mensajeRegistro, setMensajeRegistro] = useState("");
  const [errorRegistro, setErrorRegistro] = useState("");


  const resultadoEstable = (
    resultado?.letra
    && confianza !== null
    && confianza >= CONFIANZA_MINIMA
  );


  async function guardarResultado() {
    const sesion = obtenerSesion();

    if (!sesion) {
      setErrorRegistro(
        "Debes iniciar sesión para guardar el resultado."
      );
      return;
    }

    if (!idLetraObjetivo) {
      setErrorRegistro(
        "Selecciona una letra antes de registrar el resultado."
      );
      return;
    }

    if (
      !resultado?.letra
      || confianza === null
      || confianza < CONFIANZA_MINIMA
    ) {
      setErrorRegistro(
        "Espera a que el reconocimiento sea estable."
      );
      return;
    }

    setGuardando(true);
    setMensajeRegistro("");
    setErrorRegistro("");

    try {
      const respuesta = await registrarResultadoReconocimiento(
        {
          id_letra_objetivo: idLetraObjetivo,
          letra_detectada: resultado.letra,
          confianza,
        },
        sesion.access_token,
      );

      setMensajeRegistro(
        respuesta.resultado.es_correcto
          ? "Resultado guardado: la seña es correcta."
          : (
              "Resultado guardado: se detectó "
              + respuesta.resultado.letra_detectada
              + "."
            )
      );

    } catch (error) {
      setErrorRegistro(
        error instanceof ErrorApi
          ? error.message
          : "No fue posible guardar el resultado."
      );

    } finally {
      setGuardando(false);
    }
  }


  return (
    <div className="resultadoReconocimiento">
      <h4>Resultado del reconocimiento</h4>

      {mensajeError ? (
        <>
          <p role="alert">{mensajeError}</p>

          <button
            type="button"
            onClick={reintentar}
          >
            Reintentar reconocimiento
          </button>
        </>
      ) : (
        <>
          <div role="status">
            {resultado?.letra ? (
              <>
                <p>
                  Vocal detectada:{" "}
                  <strong>{resultado.letra}</strong>
                </p>

                <p>
                  Estabilidad:{" "}
                  <strong>
                    {confianza === null
                      ? "Calculando..."
                      : `${Math.round(confianza * 100)}%`}
                  </strong>
                </p>
              </>
            ) : (
              <p>
                {resultado?.mensaje
                  ?? "Esperando el primer resultado..."}
              </p>
            )}
          </div>

          <p>
            {procesando
              ? "Analizando imagen..."
              : "Reconocimiento activo"}
          </p>

          <button
            type="button"
            onClick={() => void guardarResultado()}
            disabled={
              !resultadoEstable
              || guardando
              
            }
          >
            {guardando
              ? "Guardando resultado..."
              : "Registrar intento"}
          </button>

          {mensajeRegistro && (
            <p role="status">
              {mensajeRegistro}
            </p>
          )}

          {errorRegistro && (
            <p role="alert">
              {errorRegistro}
            </p>
          )}
        </>
      )}
    </div>
  );
}


export default ResultadoReconocimiento;