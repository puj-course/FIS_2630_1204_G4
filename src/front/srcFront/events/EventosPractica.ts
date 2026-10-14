export type EventoPractica =
  | { tipo: "intentoRegistrado" }
  | { tipo: "progresoRegistrado"; idLetra: number };

export interface ObservadorPractica {
  actualizar(evento: EventoPractica): void;
}

export interface SujetoPractica {
  suscribir(observador: ObservadorPractica): void;
  desuscribir(observador: ObservadorPractica): void;
  notificar(evento: EventoPractica): void;
}

export class EventosPractica implements SujetoPractica {
  private observadores = new Set<ObservadorPractica>();

  suscribir(observador: ObservadorPractica): void {
    this.observadores.add(observador);
  }

  desuscribir(observador: ObservadorPractica): void {
    this.observadores.delete(observador);
  }

  notificar(evento: EventoPractica): void {
    for (const observador of [...this.observadores]) {
      try {
        observador.actualizar(evento);
      } catch {
        console.error(
          "No fue posible actualizar una vista de práctica."
        );
      }
    }
  }
}