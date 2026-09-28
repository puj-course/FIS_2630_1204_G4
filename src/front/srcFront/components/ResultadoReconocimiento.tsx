import {
  useState,
  type RefObject,
} from "react";

import { ErrorApi } from "../services/api";
import { obtenerSesion } from "../services/autenticacion";
import { registrarProgreso } from "../services/progreso";
import { registrarResultadoReconocimiento } from "../services/resultados";
import { useReconocimiento } from "../hooks/useReconocimiento";

import {
  crearSesionReconocimiento,
  guardarSesionReconocimiento,
  obtenerSesionReconocimiento,
} from "../services/sesiones";

import {
  obtenerIdLetra,
} from "../services/letras";

import type {
  ModoReconocimiento,
} from "../services/vision";
const CONFIANZA_MINIMA = 0.80;

interface Props {
  videoRef: RefObject<HTMLVideoElement | null>;
  idLetraObjetivo: number | null;
  modo: ModoReconocimiento;
  onReconocimientoCorrecto?: (idLetra: number) => void;
  onResultadoRegistrado?: () => void;
}

function ResultadoReconocimiento({
  videoRef,
  idLetraObjetivo,
  modo,
  onReconocimientoCorrecto,
  onResultadoRegistrado,
}: Props) {
  const {
    resultado,
    confianza,
    procesando,
    mensajeError,
    reintentar,
  } = useReconocimiento(videoRef, modo);

  const [guardando, setGuardando] = useState(false);
  const [mensajeRegistro, setMensajeRegistro] = useState("");
  const [errorRegistro, setErrorRegistro] = useState("");

  const resultadoEstable =
  Boolean(
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
  const idLetraDetectada = await obtenerIdLetra(
    resultado.letra,
  );

  if (!idLetraDetectada) {
    setErrorRegistro(
      "No se encontró la letra detectada.",
    );
    return;
  }

  let sesionReconocimiento =
    obtenerSesionReconocimiento();

  if (!sesionReconocimiento) {
    const nuevaSesion =
      await crearSesionReconocimiento(
        sesion.access_token,
      );

    sesionReconocimiento =
      nuevaSesion.sesion;

    guardarSesionReconocimiento(
      sesionReconocimiento,
    );
  }

  const respuesta = await registrarResultadoReconocimiento(
    {
      id_sesion: sesionReconocimiento.id_sesion,
      id_letra_objetivo: idLetraObjetivo,
      id_letra_detectada: idLetraDetectada,
      confianza,
    },
    sesion.access_token,
  );

      onResultadoRegistrado?.();

      if (respuesta.resultado.es_correcto) {
        setMensajeRegistro(
          "Resultado guardado: la seña es correcta."
        );

        onReconocimientoCorrecto?.(idLetraObjetivo);

        try {
          await registrarProgreso(
            { id_letra: idLetraObjetivo },
            sesion.access_token
          );

          setMensajeRegistro(
            "Resultado guardado: la seña es correcta y la letra quedó aprendida."
          );
        } catch (error) {
          setErrorRegistro(
            error instanceof ErrorApi
              ? `El resultado se guardó, pero no se pudo actualizar el progreso: ${error.message}`
              : "El resultado se guardó, pero no se pudo actualizar el progreso."
          );
        }
      } else {
        setMensajeRegistro(
  "Resultado guardado correctamente."
);
      }
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
          <p role="alert">
            {mensajeError}
          </p>

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
                  Letra detectada:{" "}
                  <strong>
                    {resultado.letra}
                  </strong>
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

          {idLetraObjetivo !== null && (
            <>
              <button
                type="button"
                className="botonRegistrarIntento"
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
        </>
      )}
    </div>
  );
}

export default ResultadoReconocimiento;