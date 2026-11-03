
import { afterEach, beforeAll, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import Aprender from "../srcFront/Aprender";

vi.mock("../srcFront/services/autenticacion", () => ({
  obtenerSesion: () => null,
}));

vi.mock("../srcFront/services/letras", () => ({
  obtenerLetras: vi.fn().mockResolvedValue([
    {
      id_letra: 1,
      letra: "A",
      descripcion: "Seña de la letra A",
      ruta_imagen: null,
    },
    {
      id_letra: 2,
      letra: "B",
      descripcion: "Seña de la letra B",
      ruta_imagen: null,
    },
  ]),
  actualizarLetra: vi.fn(),
}));

vi.mock("../srcFront/services/progreso", () => ({
  consultarEstadoLetras: vi.fn(),
}));

beforeAll(() => {
  // jsdom no implementa completamente showModal.
  Object.defineProperty(HTMLDialogElement.prototype, "showModal", {
    configurable: true,
    value: function (this: HTMLDialogElement) {
      this.setAttribute("open", "");
    },
  });
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

async function abrirDetalle() {
  render(<Aprender cambiarPagina={vi.fn()} />);

  const boton = await screen.findByRole("button", {
    name: "Ver detalle de la letra A",
  });

  fireEvent.click(boton);

  return await screen.findByRole("dialog", {
    name: "Detalle de la letra A",
  });
}

describe("Modulo Aprender", () => {
  it("muestra las letras cargadas", async () => {
    render(<Aprender cambiarPagina={vi.fn()} />);

    expect(
      await screen.findByRole("button", {
        name: "Ver detalle de la letra A",
      })
    ).toBeTruthy();

    expect(
      screen.getByRole("button", {
        name: "Ver detalle de la letra B",
      })
    ).toBeTruthy();
  });

  it("abre el detalle de una letra", async () => {
    const dialogo = await abrirDetalle();

    expect(dialogo.hasAttribute("open")).toBe(true);
    expect(screen.getByRole("button", { name: "Cerrar" })).toBeTruthy();
  });

  it("cierra el detalle con su boton", async () => {
    await abrirDetalle();

    fireEvent.click(screen.getByRole("button", { name: "Cerrar" }));

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
    });
  });

  it("cierra el detalle al pulsar el fondo", async () => {
    await abrirDetalle();

    fireEvent.click(
      screen.getByRole("button", {
        name: "Cerrar detalle de la letra",
      })
    );

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
    });
  });

  it("cierra el detalle con el evento Escape", async () => {
    const dialogo = await abrirDetalle();

    fireEvent(
      dialogo,
      new Event("cancel", {
        bubbles: true,
        cancelable: true,
      })
    );

    await waitFor(() => {
      expect(screen.queryByRole("dialog")).toBeNull();
    });
  });

  it("permite navegar a la siguiente letra", async () => {
    await abrirDetalle();

    fireEvent.click(
      screen.getByRole("button", { name: "Siguiente letra" })
    );

    expect(
      await screen.findByRole("dialog", {
        name: "Detalle de la letra B",
      })
    ).toBeTruthy();
  });
});
