interface Props {
  cambiarPagina: (pagina: string) => void;
}

function Home({ cambiarPagina }: Props) {
  return (
    <div className="pantalla">
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