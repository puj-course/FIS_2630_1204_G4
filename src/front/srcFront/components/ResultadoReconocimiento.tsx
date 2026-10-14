import {
  useEffect,
  useRef,
  useState,
  type RefObject,
} from "react";

import type { SujetoPractica } from "../events/EventosPractica";
import { useReconocimiento } from "../hooks/useReconocimiento";
import { obtenerSesion } from "../services/autenticacion";
import { FachadaRegistroPractica } from "../services/FachadaRegistroPractica";
import type { ModoReconocimiento } from "../services/vision";

interface Props {
  videoRef: RefObject<HTMLVideoElement | null>;
  idLetraObjetivo: number | null;
  modo: ModoReconocimiento;
  eventosPractica: SujetoPractica;
}

function ResultadoReconocimiento({
  videoRef,
  idLetraObjetivo,
  modo,
  eventosPractica,
}: Props) {
  const {
    resultado,
    confianza,
    intentoReconocido,
    procesando,
    mensajeError,
    reintentar,
  } = useReconocimiento(videoRef, modo);

  const [fachada] = useState(
    () => new FachadaRegistroPractica(),
  );

  const [guardando, setGuardando] = useState(false);
  const [mensajeRegistro, setMensajeRegistro] = useState("");
  const [errorRegistro, setErrorRegistro] = useState("");
  const [registroPausado, setRegistroPausado] = useState(false);

  const ultimoIntento = useRef<string | null>(null);
  const colaRegistros = useRef<Promise<void>>(Promise.resolve());
  const pausado = useRef(false);
  const contexto = useRef({ activo: false });

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

    let token: string | null = null;
    let errorSesion: Error | null = null;

    try {
      const sesion = obtenerSesion();

      if (!sesion) {
        throw new Error(
          "Debes iniciar sesión para registrar los intentos.",
        );
      }

      token = sesion.access_token;
    } catch (error) {
      errorSesion = error instanceof Error
        ? error
        : new Error(
            "No fue posible obtener la sesión del usuario.",
          );
    }

    async function guardarIntento() {
      if (!contextoActual.activo || pausado.current) {
        return;
      }

      let resultadoGuardado = false;

      setGuardando(true);
      setMensajeRegistro("");
      setErrorRegistro("");

      try {
        if (errorSesion !== null) {
          throw errorSesion;
        }

        if (!token) {
          throw new Error(
            "Debes iniciar sesión para registrar los intentos.",
          );
        }

        const respuesta = await fachada.registrarIntento({
          token,
          idLetraObjetivo: objetivo,
          letraDetectada: deteccion.letra,
          confianza: deteccion.confianza,
          sigueActivo: () => contextoActual.activo,
        });

        if (respuesta === null) {
          return;
        }

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

        eventosPractica.notificar({ tipo: "intentoRegistrado" });

        if (respuesta.resultado.es_correcto) {
          await fachada.registrarProgreso(
            objetivo,
            token,
          );

          if (
            contextoActual.activo
            && obtenerSesion()?.access_token === token
          ) {
            setMensajeRegistro(
              "Intento guardado automáticamente y progreso actualizado.",
            );
            eventosPractica.notificar({
              tipo: "progresoRegistrado",
              idLetra: objetivo,
            });
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

        pausado.current = true;
        setRegistroPausado(true);
        setErrorRegistro(detalle);
      } finally {
        if (contextoActual.activo) {
          setGuardando(false);
        }
      }
    }

    colaRegistros.current = colaRegistros.current.then(
      guardarIntento,
    );
  }, [
    intentoReconocido,
    idLetraObjetivo,
    modo,
    eventosPractica,
    fachada,
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