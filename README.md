# SignIA 💙
**"Aprender para comunicar, comunicar para incluir."**

## Descripción
**SignIA** es una plataforma web multiusuario orientada al aprendizaje y reconocimiento del alfabeto de la **Lengua de Señas Colombiana (LSC)** mediante visión por computador, la plataforma facilita la práctica del alfabeto de la LSC utilizando la cámara del dispositivo, permitiendo identificar las señas realizadas por el usuario y mostrar la letra correspondiente en tiempo real.

SignIA surge como respuesta a las barreras de comunicación existentes entre personas sordas y oyentes y a la necesidad de generar herramientas tecnológicas que permitan ampliar el conocimiento básico de la LSC, la plataforma busca promover el aprendizaje autónomo, la sensibilización frente a la comunidad sorda y el uso de la tecnología como herramienta para contribuir a una comunicación más inclusiva.

----

## Equipo del Proyecto

El equipo de **SignIA** se encuentra organizado mediante roles definidos para apoyar la gestión, planificación, calidad y desarrollo del proyecto.

| Integrante | Rol | GitHub |
|---|---|---|
| **Isabel Gutiérrez** | Scrum Master | [@isabelsgp](https://github.com/isabelsgp) |
| **Juan Diego Arevalo** | Product Owner | [@Juan123839](https://github.com/Juan123839) |
| **Juan Pablo Vanegas** | Sprint Planner | [@juanpvanegasvelandia02-ship-it](https://github.com/ujuanpvanegasvelandia02-ship-it) |
| **David Vallejo** | Configuration Manager | [@David-wallpaper](https://github.com/David-wallpaper) |
| **Juan Diego Arevalo** | QA Lead | [@Juan123839](https://github.com/Juan123839) |
| **Oscar Martinez Mantilla** | DevOps Engineer | [@martinezm-oe](https://github.com/martinezm-oe) |

---

## Tecnologías Utilizadas

- **Frontend:** React + TypeScript + Vite
- **Librería de componentes visuales:** React Icons
- **Backend:** Python – FastAPI
- **Base de Datos:** PostgreSQL
- **Visión por Computador:** OpenCV + MediaPipe
- **Procesamiento de datos:** Pandas
- **Gestión de dependencias Frontend:** npm + package-lock.json
- **Gestión de dependencias Backend:** pip + requirements.txt + requirements.lock.txt
- **Control de versiones:** Git

------

## Estructura del Proyecto

```text
FIS_2630_1204_G4/
│
├── app/
│   ├── main.py
│   │   └── Punto de entrada principal del backend con FastAPI.
│   │
│   ├── routes/
│   │   └── Define las rutas y endpoints principales de la API.
│   │
│   ├── controllers/
│   │   └── Procesa las solicitudes recibidas desde las rutas.
│   │
│   ├── services/
│   │   └── Contiene la lógica de negocio y servicios reutilizables.
│   │
│   └── vision/
│       └── Contiene el procesamiento con OpenCV, MediaPipe y reconocimiento.
│
├── conf/
│   ├── config.py
│   │   └── Contiene parámetros generales de configuración.
│   │
│   ├── database.py
│   │   └── Configura la conexión con PostgreSQL.
│   │
│   └── environment.example
│       └── Ejemplo de las variables de entorno necesarias.
│
├── docs/
│   ├── architecture.md
│   │   └── Describe la arquitectura general de SignIA.
│   │
│   ├── api.md
│   │   └── Documenta los endpoints de la API.
│   │
│   ├── installation.md
│   │   └── Explica la instalación y configuración del proyecto.
│   │
│   └── user_guide.md
│       └── Guía básica para utilizar SignIA.
│
├── scripts/
│   ├── setup.sh
│   │   └── Automatiza la configuración inicial.
│   │
│   ├── start.sh
│   │   └── Permite iniciar la aplicación.
│   │
│   ├── test.sh
│   │   └── Ejecuta las pruebas.
│   │
│   └── deploy.sh
│       └── Automatiza tareas relacionadas con despliegue.
│
├── src/
│   ├── models/
│   │   └── Define los modelos de datos del sistema.
│   │
│   ├── schemas/
│   │   └── Define los esquemas utilizados para validación de datos.
│   │
│   ├── utils/
│   │   └── Contiene funciones auxiliares reutilizables.
│   │
│   ├── middleware/
│   │   └── Contiene funciones ejecutadas durante las solicitudes.
│   │
│   └── tests/
│       └── Contiene las pruebas unitarias y de integración.
│
├── web/
│   ├── package.json
│   │   └── Define las dependencias y scripts del frontend.
│   │
│   ├── public/
│   │   └── Contiene recursos públicos del frontend.
│   │
│   └── src/
│       ├── assets/
│       │   └── Imágenes e iconos utilizados por la aplicación.
│       ├── components/
│       │   └── Componentes reutilizables de React.
│       ├── pages/
│       │   └── Páginas principales de la plataforma.
│       └── services/
│           └── Comunicación del frontend con la API.
│
├── temp/
│   ├── .gitkeep
│   └── uploads/
│       └── Archivos temporales utilizados durante la ejecución.
│
├── requirements.txt
│   └── Dependencias de Python utilizadas por el backend.
│
├── BOILERPLATE_template.md
│   └── Documento base proporcionado para organizar el proyecto.
│
├── CONTRIBUTING.md
│   └── Normas para contribuir al repositorio.
│
├── LICENSE
│   └── Licencia del proyecto.
│
├── README.md
│   └── Documento principal de SignIA.
│
├── .gitignore
│   └── Archivos y carpetas que Git no debe versionar.
│
└── .env.example
    └── Plantilla de variables de entorno.


```

---

## Instalación y Ejecución
**Requisitos**
- Docker y Docker Compose
- Git
- Python 3.10+
- Node.js
- npm
- PostgreSQL

## Clonar el repositorio
```text
git clone https://github.com/puj-course/FIS_2630_1204_G4.git
cd SignIA
```

## Ejecución con Docker
```text
docker-compose up --build
```
prueba conflicto
## Ejecución de pruebas
```text
docker-compose run backend mvn test
docker-compose run ai-model pytest
```

---

## Contexto Académico
- **Asignatura:** Fundamentos de Ingeniería de Software
- **Docente:** Luis Gabriel Moreno Sandoval, PhD
- **Contacto:** morenoluis@javeriana.edu.co

---

## Contacto

**Equipo de desarrollo:**

**Isabel Gutiérrez**  
Estudiante de Ingeniería en Sistemas, Pontificia Universidad Javeriana  
📧 isabels-gutierrez@javeriana.edu.co  

**Juan Diego Arevalo**  
Estudiante de Ingeniería en Sistemas, Pontificia Universidad Javeriana  
📧 jd.arevalo@javeriana.edu.co  

**Juan Pablo Vanegas**  
Estudiante de Ingeniería de Sistemas, Pontificia Universidad Javeriana  
Correo: Juanpvanegasvelandia02@gmail.com

**David Vallejo**  
Estudiante de Ingeniería en Sistemas, Pontificia Universidad Javeriana  
📧 vallejo-david@javeriana.edu.co 

**Oscar Eduardo Martinez Mantilla**  
Estudiante de Ingeniería en Sistemas, Pontificia Universidad Javeriana  
📧 martinezm.oe@javeriana.edu.co  


--- 

## Licencia
Proyecto desarrollado con fines académicos.

---
