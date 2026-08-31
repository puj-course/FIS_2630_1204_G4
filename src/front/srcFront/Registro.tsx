import { useState } from 'react';

interface Props {
  cambiarPagina: (pagina: string) => void;
}

function Registro({ cambiarPagina }: Props) {
  const [nombre, setNombre] = useState('');
  const [correo, setCorreo] = useState('');
  const [contrasena, setContrasena] = useState('');
  const [confirmar, setConfirmar] = useState('');

  const manejarRegistro = () => {
    if (contrasena !== confirmar) {
      alert('Las contraseñas no coinciden');
      return;
    }
    console.log('Registro simulado:', nombre, correo);
    cambiarPagina('login');
  };

  return (
    <div className="pantalla">
      <h1 className="logo">SignIA</h1>
      <h2>Crear cuenta</h2>

      <input
        type="text"
        placeholder="Nombre completo"
        value={nombre}
        onChange={(e) => setNombre(e.target.value)}
      />

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

      <input
        type="password"
        placeholder="Confirmar contraseña"
        value={confirmar}
        onChange={(e) => setConfirmar(e.target.value)}
      />

      <button onClick={manejarRegistro}>Registrarse</button>

      <p>
        ¿Ya tienes cuenta?{' '}
        <span className="enlace" onClick={() => cambiarPagina('login')}>
          Inicia sesión
        </span>
      </p>
    </div>
  );
}

export default Registro;