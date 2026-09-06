const URL_BASE_API = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export interface EstadoBackend {
  estado: string;
  mensaje: string;
}

interface DetalleError {
  detail?: string;
}

export class ErrorApi extends Error {
  codigoEstado?: number;

  constructor(mensaje: string, codigoEstado?: number) {
    super(mensaje);
    this.name = "ErrorApi";
    this.codigoEstado = codigoEstado;
  }
}

export async function solicitarApi<T>(
  ruta: string,
  opciones: RequestInit = {}
): Promise<T> {
  const rutaNormalizada = ruta.startsWith("/") ? ruta : `/${ruta}`;
  const headers = new Headers(opciones.headers);

  if (opciones.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  let respuesta: Response;

  try {
    respuesta = await fetch(
      `${URL_BASE_API}${rutaNormalizada}`,
      {
        ...opciones,
        headers
      }
    );
  } catch {
    throw new ErrorApi(
      "No fue posible establecer comunicación con el backend."
    );
  }

  if (!respuesta.ok) {
    const cuerpo = await respuesta
      .json()
      .catch(() => null) as DetalleError | null;

    throw new ErrorApi(
      cuerpo?.detail
        ?? `El backend respondió con el estado ${respuesta.status}.`,
      respuesta.status
    );
  }

  if (respuesta.status === 204) {
    return undefined as T;
  }

  return await respuesta.json() as T;
}

export function comprobarConexionBackend(): Promise<EstadoBackend> {
  return solicitarApi<EstadoBackend>("/health");
}

export { URL_BASE_API };