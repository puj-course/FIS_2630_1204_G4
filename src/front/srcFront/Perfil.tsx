import { useEffect, useState } from "react";

import { ErrorApi } from "./services/api";
import { obtenerSesion } from "./services/autenticacion";
import {
  consultarPerfil,
  type PerfilUsuario
} from "./services/perfil";


function Perfil() {
  const [perfil, setPerfil] = useState<PerfilUsuario | null>(
    null
  );
  const [cargando, setCargando] = useState(true);
  const [mensajeError, setMensajeError] = useState("");

  useEffect(() => {
    let componenteActivo = true;

    async function cargarPerfil() {
      const sesion = obtenerSesion();

      if (!sesion) {
        if (componenteActivo) {
          setMensajeError(
            "No se encontró una sesión activa."
          );
          setCargando(false);
        }

        return;
      }

      try {
        const perfilConsultado = await consultarPerfil(
          sesion.access_token
        );

        if (componenteActivo) {
          setPerfil(perfilConsultado);
        }

      } catch (error) {
        if (componenteActivo) {
          setMensajeError(
            error instanceof ErrorApi
              ? error.message
              : "No fue posible cargar el perfil."
          );
        }

      } finally {
        if (componenteActivo) {
          setCargando(false);
        }
      }
    }

    void cargarPerfil();

    return () => {
      componenteActivo = false;
    };
  }, []);

  if (cargando) {
    return (
      <div className="perfil estadoPerfil">
        <p>Cargando información del perfil...</p>
      </div>
    );
  }

  if (mensajeError || !perfil) {
    return (
      <div className="perfil estadoPerfil">
        <h2>No fue posible cargar el perfil</h2>
        <p role="alert">
          {mensajeError || "No se encontró información."}
        </p>
      </div>
    );
  }

  const porcentaje = Math.min(
    100,
    Math.max(0, perfil.progreso.porcentaje_progreso)
  );

  const inicial = (
    perfil.nombre.trim().charAt(0) || "U"
  ).toUpperCase();

  return (
    <div className="perfil">
      <section className="perfilHeader">
        <div className="usuario">
          <div className="avatar" aria-hidden="true">
            {inicial}
          </div>

          <div>
            <h2>{perfil.nombre}</h2>
            <p>{perfil.correo}</p>
          </div>
        </div>

        <span className="rolUsuario">
          {perfil.rol === "administrador"
            ? "Administrador"
            : "Usuario"}
        </span>
      </section>

      <section className="progreso progresoPerfil">
        <div className="encabezadoProgreso">
          <div>
            <h2>Progreso en el alfabeto LSC</h2>
            <p>
              Avance calculado a partir de las letras dominadas.
            </p>
          </div>

          <strong className="porcentajeProgreso">
            {porcentaje.toFixed(2)}%
          </strong>
        </div>

        <div
          className="barraProgresoPerfil"
          role="progressbar"
          aria-label="Porcentaje de progreso"
          aria-valuemin={0}
          aria-valuemax={100}
          aria-valuenow={porcentaje}
        >
          <div
            className="rellenoProgresoPerfil"
            style={{ width: `${porcentaje}%` }}
          />
        </div>

        <div className="resumenProgreso">
          <div className="datoProgreso">
            <span>Letras disponibles</span>
            <strong>{perfil.progreso.total_letras}</strong>
          </div>

          <div className="datoProgreso">
            <span>Letras iniciadas</span>
            <strong>{perfil.progreso.letras_iniciadas}</strong>
          </div>

          <div className="datoProgreso">
            <span>Letras dominadas</span>
            <strong>{perfil.progreso.letras_dominadas}</strong>
          </div>

          <div className="datoProgreso">
            <span>Intentos realizados</span>
            <strong>{perfil.progreso.cantidad_intentos}</strong>
          </div>

          <div className="datoProgreso">
            <span>Aciertos obtenidos</span>
            <strong>{perfil.progreso.cantidad_aciertos}</strong>
          </div>
        </div>

        {perfil.progreso.letras_iniciadas === 0 && (
          <p className="mensajeSinProgreso">
            Aún no tienes progreso registrado. Comienza una
            práctica para avanzar.
          </p>
        )}
      </section>
    </div>
  );
}

export default Perfil;