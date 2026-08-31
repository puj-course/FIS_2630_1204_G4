import { useState } from 'react';

interface Props {
  cambiarPagina: (pagina: string) => void;
}

function Login({ cambiarPagina }: Props) {
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');

  const manejarLogin = () => {
    // Por ahora simulado, sin backend
    console.log('Login simulado:', correo);
    cambiarPagina('home');
  };

  return (
    <div className="pantalla">
      <h1 className="logo">SignIA</h1>
      <h2>Iniciar sesión</h2>

      <input
        type="email"
        placeholder="Correo electrónico"
        value={correo}
        onChange={(e) => setCorreo(e.target.value)}
      />

      <input
        type="password"
        placeholder="Contraseña"
        value={contrasena}
        onChange={(e) => setContrasena(e.target.value)}
      />

      <button onClick={manejarLogin}>Iniciar sesión</button>

      <p>
        ¿No tienes cuenta?{' '}
        <span className="enlace" onClick={() => cambiarPagina('registro')}>
          Regístrate
        </span>
      </p>
    </div>
  );
}

export default Login;