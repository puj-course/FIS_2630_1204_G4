import { FaHistory, FaTrash } from "react-icons/fa";
import type { ResultadoRegistrado } from "../services/resultados";

interface Props {
  historial: ResultadoRegistrado[];
  cargando: boolean;
  error: string;
  limpiando: boolean;
  onLimpiar: () => void;
}

function formatearFecha(fecha: string): string {
  return new Date(fecha).toLocaleString("es-CO", {
    dateStyle: "short",
    timeStyle: "short"
  });
}

function HistorialReconocimiento({
  historial,
  cargando,
  error,
  limpiando,
  onLimpiar,
}: Props) {
  return (
    <section className="panelUltimasSenas">
      <div className="tituloUltimasSenas">
        <div>
          <FaHistory />
          <h2>Historial de reconocimiento</h2>
        </div>

        <button
          type="button"
          className="botonLimpiarHistorial"
          onClick={onLimpiar}
          disabled={historial.length === 0 || limpiando}
        >
          <FaTrash />
          {limpiando ? "Limpiando..." : "Limpiar"}
        </button>
      </div>

      <div className="contenedorHistorialScroll">
        {cargando ? (
          <div className="historialReconocimientoVacio">
            <p>Cargando historial...</p>
          </div>
        ) : error ? (
          <div className="historialReconocimientoVacio">
            <p role="alert">{error}</p>
          </div>
        ) : historial.length === 0 ? (
          <div className="historialReconocimientoVacio">
            <FaHistory />
            <p>Aún no tienes intentos registrados.</p>
          </div>
        ) : (
          <div className="listaHistorialReconocimiento">
            {historial.map((resultado) => (
              <div
                className={
                  resultado.es_correcto
                    ? "itemHistorialReconocimiento historialCorrecto"
                    : "itemHistorialReconocimiento historialIncorrecto"
                }
                key={resultado.id_resultado}
              >
                <div className="letraHistorial">
                  {resultado.letra_detectada}
                </div>

                <div className="detalleHistorial">
                  <strong>
                    {resultado.es_correcto
                      ? "Seña correcta"
                      : "Seña incorrecta"}
                  </strong>
                  <span>
                    Objetivo: {resultado.letra_objetivo}
                  </span>
                  <span>
                    Detectada: {resultado.letra_detectada}
                  </span>
                  <span>
                    Fecha:{" "}
                    <time dateTime={resultado.fecha_resultado}>
                      {formatearFecha(resultado.fecha_resultado)}
                    </time>
                  </span>
                </div>

                <div className="confianzaHistorial">
                  {Math.round(resultado.confianza * 100)}%
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

export default HistorialReconocimiento;