export interface PreguntaFrecuente {
  pregunta: string;
  respuesta: string;
}

export const preguntasFrecuentes: PreguntaFrecuente[] = [
  {
    pregunta: "¿Cómo activo la cámara para practicar?",
    respuesta:
      "Entra a la sección \"Practicar\" y haz clic en el botón \"Activar cámara\". El navegador te pedirá permiso para usarla; acéptalo para que el reconocimiento en tiempo real funcione."
  },
  {
    pregunta: "¿Por qué no reconoce mi seña correctamente?",
    respuesta:
      "Asegúrate de tener buena iluminación, un fondo despejado detrás de tu mano y de mantenerla completa dentro del encuadre de la cámara. Revisa también la guía de cada letra en \"Aprender\" antes de practicarla."
  },
  {
    pregunta: "¿Cómo se calcula mi progreso en el alfabeto?",
    respuesta:
      "Tu progreso se basa en las letras que has practicado: cada una pasa de \"pendiente\" a \"iniciada\" y luego a \"dominada\" según tus aciertos. Puedes ver el detalle completo en tu perfil."
  },
  {
    pregunta: "¿Puedo cambiar cuántas señas practico cada día?",
    respuesta:
      "Sí. En tu perfil, en la sección \"Meta diaria de práctica\", puedes elegir entre 5, 10, 15 o 20 señas por día."
  },
  {
    pregunta: "¿Qué hago si olvidé mi contraseña?",
    respuesta:
      "En la pantalla de inicio de sesión, usa la opción \"¿Olvidaste tu contraseña?\" para recibir un enlace de recuperación en tu correo registrado."
  },
  {
    pregunta: "¿Puedo volver a ver la guía de bienvenida?",
    respuesta:
      "Sí. Desde la pantalla de inicio (Home), haz clic en el botón \"¿Cómo funciona?\" para repasar los pasos básicos de SignIA en cualquier momento."
  }
];