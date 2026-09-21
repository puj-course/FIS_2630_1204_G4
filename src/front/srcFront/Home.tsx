import Bienvenida from "./components/Bienvenida";
import { useEffect, useState } from "react";
import { obtenerSesion } from "./services/autenticacion";
interface Props {
  cambiarPagina: (pagina: string) => void;
}
function claveBienvenidaVista(idUsuario: number): string {
  return `signia_bienvenida_vista_${idUsuario}`;
}

function Home({ cambiarPagina }: Props) {
  const [mostrarBienvenida, setMostrarBienvenida] = useState(false);

  useEffect(() => {
    const sesion = obtenerSesion();

    if (!sesion) {
      return;
    }

    const yaVista = localStorage.getItem(
      claveBienvenidaVista(sesion.usuario.id_usuario)
    );

    if (!yaVista) {
      setMostrarBienvenida(true);
    }
  }, []);

  function cerrarBienvenida() {
    const sesion = obtenerSesion();

    if (sesion) {
      localStorage.setItem(
        claveBienvenidaVista(sesion.usuario.id_usuario),
        "true"
      );
    }

    setMostrarBienvenida(false);
  }
  return (
    <div className="pantalla">
      {mostrarBienvenida && (
        <Bienvenida onCerrar={cerrarBienvenida} />
      )}
      <h1 className="logo">SignIA</h1>
      <h2>Bienvenido a SignIA</h2>
      <p className="lema">"Aprender para comunicar, comunicar para incluir."</p>
      <p>
        Aprende y practica el alfabeto de la Lengua de Señas Colombiana (LSC)
        usando la cámara de tu dispositivo, en tiempo real.
      </p>

      <div className="tarjetas">
        <div className="tarjeta" onClick={() => cambiarPagina('practica')}>
          <h3>Practicar señas</h3>
          <p>Empieza a reconocer letras con tu cámara</p>
        </div>

        <div className="tarjeta" onClick={() => cambiarPagina('perfil')}>
          <h3>Mi perfil</h3>
          <p>Revisa tu progreso de aprendizaje</p>
        </div>
      </div>
    </div>
  );
}

export default Home;