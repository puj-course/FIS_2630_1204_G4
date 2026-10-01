import {
  useEffect,
  useRef,
  useState,
  type RefObject,
} from "react";

import { useReconocimiento } from "../hooks/useReconocimiento";
import { ErrorApi } from "../services/api";
import { obtenerSesion } from "../services/autenticacion";
import { obtenerIdLetra } from "../services/letras";
import { registrarProgreso } from "../services/progreso";
import { registrarResultadoReconocimiento } from "../services/resultados";

import {
  crearSesionReconocimiento,
  guardarSesionReconocimiento,
  limpiarSesionReconocimiento,
  obtenerSesionReconocimiento,
} from "../services/sesiones";

import type {
  ModoReconocimiento,
} from "../services/vision";

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
    intentoReconocido,
    procesando,
    mensajeError,
    reintentar,
  } = useReconocimiento(videoRef, modo);

  const [guardando, setGuardando] = useState(false);
  const [mensajeRegistro, setMensajeRegistro] = useState("");
  const [errorRegistro, setErrorRegistro] = useState("");
  const [registroPausado, setRegistroPausado] = useState(false);

  const ultimoIntento = useRef<string | null>(null);
  const colaRegistros = useRef<Promise<void>>(Promise.resolve());
  const pausado = useRef(false);
  const contexto = useRef({ activo: false });

  const callbacks = useRef({
    onReconocimientoCorrecto,
    onResultadoRegistrado,
  });

  useEffect(() => {
    callbacks.current = {
      onReconocimientoCorrecto,
      onResultadoRegistrado,
    };
  }, [
    onReconocimientoCorrecto,
    onResultadoRegistrado,
  ]);

  useEffect(() => {
    const actual = { activo: true };
    contexto.current = actual;

    return () => {
      actual.activo = false;
    };
  }, []);

  useEffect(() => {
    if (
      !intentoReconocido
      || idLetraObjetivo === null
      || intentoReconocido.modo !== modo
      || ultimoIntento.current === intentoReconocido.id
      || pausado.current
    ) {
      return;
    }

    const deteccion = intentoReconocido;
    const objetivo = idLetraObjetivo;
    const contextoActual = contexto.current;

    ultimoIntento.current = deteccion.id;

    let token: string;

    try {
      const sesion = obtenerSesion();

      if (!sesion) {
        throw new Error(
          "Debes iniciar sesión para registrar los intentos.",
        );
      }

      token = sesion.access_token;
    } catch (error) {
      pausado.current = true;
      setRegistroPausado(true);
      setErrorRegistro(
        error instanceof Error
          ? error.message
          : "No fue posible obtener la sesión del usuario.",
      );
      return;
    }

    async function guardarIntento() {
      if (!contextoActual.activo || pausado.current) {
        return;
      }

      let resultadoGuardado = false;
      let idSesionUtilizada: number | null = null;

      setGuardando(true);
      setMensajeRegistro("");
      setErrorRegistro("");

      try {
        if (obtenerSesion()?.access_token !== token) {
          throw new Error(
            "La sesión del usuario cambió. Inicia otra práctica.",
          );
        }

        if (
          !Number.isInteger(objetivo)
          || objetivo <= 0
          || !Number.isFinite(deteccion.confianza)
          || deteccion.confianza < 0.8
          || deteccion.confianza > 1
        ) {
          throw new Error(
            "La detección no contiene datos válidos para registrarla.",
          );
        }

        const idLetraDetectada = await obtenerIdLetra(
          deteccion.letra,
        );

        if (!contextoActual.activo) {
          return;
        }

        if (
          !Number.isInteger(idLetraDetectada)
          || !idLetraDetectada
          || idLetraDetectada <= 0
        ) {
          throw new Error(
            "No se encontró la letra detectada en el alfabeto.",
          );
        }

        let sesionReconocimiento =
          obtenerSesionReconocimiento();

        if (
          !sesionReconocimiento
          || sesionReconocimiento.estado !== "activa"
          || sesionReconocimiento.fecha_fin !== null
        ) {
          if (obtenerSesion()?.access_token !== token) {
            throw new Error(
              "La sesión del usuario cambió. Inicia otra práctica.",
            );
          }

          const nuevaSesion = await crearSesionReconocimiento(
            token,
          );

          if (
            !contextoActual.activo
            || obtenerSesion()?.access_token !== token
          ) {
            return;
          }

          sesionReconocimiento = nuevaSesion.sesion;
          guardarSesionReconocimiento(sesionReconocimiento);
        }

        if (!contextoActual.activo) {
          return;
        }

        if (obtenerSesion()?.access_token !== token) {
          throw new Error(
            "La sesión del usuario cambió. Inicia otra práctica.",
          );
        }

        idSesionUtilizada = sesionReconocimiento.id_sesion;

        const respuesta = await registrarResultadoReconocimiento(
          {
            id_sesion: idSesionUtilizada,
            id_letra_objetivo: objetivo,
            id_letra_detectada: idLetraDetectada,
            confianza: deteccion.confianza,
          },
          token,
        );

        resultadoGuardado = true;

        if (
          !contextoActual.activo
          || obtenerSesion()?.access_token !== token
        ) {
          return;
        }

        setMensajeRegistro(
          respuesta.resultado.es_correcto
            ? "Intento guardado automáticamente: seña correcta."
            : "Intento guardado automáticamente: la seña no coincide con la letra objetivo.",
        );

        callbacks.current.onResultadoRegistrado?.();

        if (respuesta.resultado.es_correcto) {
          callbacks.current.onReconocimientoCorrecto?.(objetivo);

          // Conserva la actualización de progreso que ya existía.
          await registrarProgreso(
            { id_letra: objetivo },
            token,
          );

          if (
            contextoActual.activo
            && obtenerSesion()?.access_token === token
          ) {
            setMensajeRegistro(
              "Intento guardado automáticamente y progreso actualizado.",
            );
          }
        }
      } catch (error) {
        if (!contextoActual.activo) {
          return;
        }

        const detalle = error instanceof Error
          ? error.message
          : "Ocurrió un error inesperado.";

        if (resultadoGuardado) {
          setErrorRegistro(
            `El intento se guardó, pero no se pudo completar la actualización de la pantalla o del progreso: ${detalle}`,
          );
          return;
        }

        // Evita repetir automáticamente una solicitud cuyo
        // resultado podría haberse guardado antes de perder la conexión.
        pausado.current = true;
        setRegistroPausado(true);
        setErrorRegistro(detalle);

        if (
          error instanceof ErrorApi
          && (
            error.codigoEstado === 403
            || error.codigoEstado === 409
          )
          && idSesionUtilizada !== null
        ) {
          try {
            const almacenada = obtenerSesionReconocimiento();

            if (almacenada?.id_sesion === idSesionUtilizada) {
              limpiarSesionReconocimiento();
            }
          } catch {
            // Conserva el mensaje del error original.
          }
        }
      } finally {
        if (contextoActual.activo) {
          setGuardando(false);
        }
      }
    }

    // Procesa los intentos en orden, sin enviar dos al mismo tiempo.
    colaRegistros.current = colaRegistros.current.then(
      guardarIntento,
    );
  }, [
    intentoReconocido,
    idLetraObjetivo,
    modo,
  ]);

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
        </>
      )}

      {idLetraObjetivo !== null && (
        <>
          <p role="status">
            {registroPausado
              ? "Registro automático pausado."
              : guardando
                ? "Guardando intento..."
                : "Los intentos se registran automáticamente al reconocer una seña estable."}
          </p>

          <p>
            Para repetir la misma seña, retira la mano
            hasta que deje de reconocerse y vuelve a realizarla.
          </p>

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

          {registroPausado && (
            <p>
              Revisa el historial antes de continuar.
              Una vez resuelto el error, apaga y activa
              la cámara para iniciar otra práctica.
            </p>
          )}
        </>
      )}
    </div>
  );
}

export default ResultadoReconocimiento;