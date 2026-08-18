# SignIA 💙
**"Aprender para comunicar, comunicar para incluir."**

## Descripción
**SignIA** es una plataforma web multiusuario orientada al aprendizaje y reconocimiento del alfabeto de la **Lengua de Señas Colombiana (LSC)** mediante visión por computador, la plataforma facilita la práctica del alfabeto de la LSC utilizando la cámara del dispositivo, permitiendo identificar las señas realizadas por el usuario y mostrar la letra correspondiente en tiempo real.

SignIA surge como respuesta a las barreras de comunicación existentes entre personas sordas y oyentes y a la necesidad de generar herramientas tecnológicas que permitan ampliar el conocimiento básico de la LSC, la plataforma busca promover el aprendizaje autónomo, la sensibilización frente a la comunidad sorda y el uso de la tecnología como herramienta para contribuir a una comunicación más inclusiva.

----

## Equipo del Proyecto
| Nombre                  | Rol                    | GitHub / Perfil |
|-------------------------|------------------------|--------------------------------------------|
| Isabel Gutiérrez        | Scrum Master           | github.com/isabelsgp |
| Juan Diego Arevalo      | Product Owner          | github.com/Juan123839 |
| Juan Pablo Vanegas      | Sprint Planner         | github.com/ujuanpvanegasvelandia02-ship-it |
| David Vallejo           | Configuration Manager  | github.com/David-wallpaper |
| Juan Diego Arevalo      | QA Lead                | github.com/Juan123839 |
| Oscar Martinez Mantilla | DevOps Engineer        | github.com/martinezm-oe |

---

## Tecnologías Utilizadas

- **Frontend:** React + JavaScript
- **Backend:** Python – FastAPI
- **Base de Datos:** PostgreSQL
- **Visión por Computador:** OpenCV + MediaPipe
- **Procesamiento de datos:** Pandas
- **Control de versiones:** Git

----

## Estructura del Proyecto

```text
FIS_2630_1204_G4/
│
├── app/
│   ├── main.py
│   │   └── Punto de entrada principal del backend desarrollado con FastAPI.
│   │
│   ├── routes/
│   │   └── Define las rutas y endpoints principales de la API.
│   │
│   ├── controllers/
│   │   └── Procesa las solicitudes recibidas por la aplicación.
│   │
│   ├── services/
│   │   └── Contiene la lógica de negocio y servicios reutilizables.
│   │
│   └── vision/
│       └── Contiene el procesamiento con OpenCV, MediaPipe y clasificación.
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
│   │   └── Describe la arquitectura general del sistema.
│   │
│   ├── api.md
│   │   └── Documenta los endpoints, parámetros y respuestas de la API.
│   │
│   ├── installation.md
│   │   └── Explica cómo instalar y configurar el proyecto.
│   │
│   └── user_guide.md
│       └── Guía básica para el uso de SignIA.
│
├── scripts/
│   ├── setup.sh
│   │   └── Automatiza la configuración inicial del proyecto.
│   │
│   ├── start.sh
│   │   └── Permite iniciar la aplicación.
│   │
│   ├── test.sh
│   │   └── Ejecuta las pruebas automatizadas.
│   │
│   └── deploy.sh
│       └── Automatiza tareas relacionadas con el despliegue.
│
├── src/
│   ├── models/
│   │   └── Define los modelos de datos utilizados por el sistema.
│   │
│   ├── schemas/
│   │   └── Define los esquemas utilizados para validar los datos.
│   │
│   ├── utils/
│   │   └── Contiene funciones auxiliares reutilizables.
│   │
│   ├── middleware/
│   │   └── Contiene funciones ejecutadas durante el procesamiento de solicitudes.
│   │
│   └── tests/
│       └── Contiene pruebas unitarias y de integración.
│
├── web/
│   ├── package.json
│   │   └── Define las dependencias y scripts del frontend.
│   │
│   ├── public/
│   │   └── Contiene los recursos públicos de la aplicación web.
│   │
│   └── src/
│       ├── assets/
│       │   └── Recursos gráficos utilizados por la aplicación.
│       │
│       ├── components/
│       │   └── Componentes reutilizables de React.
│       │
│       ├── pages/
│       │   └── Páginas principales de la plataforma.
│       │
│       └── services/
│           └── Gestiona la comunicación del frontend con la API.
│
├── temp/
│   ├── .gitkeep
│   │   └── Permite conservar la carpeta temporal dentro del repositorio.
│   │
│   └── uploads/
│       └── Archivos temporales utilizados durante la ejecución.
│
├── requirements.txt
│   └── Define las dependencias utilizadas por el backend en Python.
│
├── BOILERPLATE_template.md
│   └── Plantilla base utilizada como referencia para organizar el repositorio.
│
├── CONTRIBUTING.md
│   └── Define las normas y recomendaciones para contribuir al proyecto.
│
├── LICENSE
│   └── Especifica la licencia del proyecto.
│
<<<<<<< HEAD
└── README.md
    └── Documento principal con la descripción, tecnologías, instalación y estructura de SignIA.
=======
├── README.md
│   └── Documento principal con la descripción, instalación y características de SignIA.
│
├── .gitignore
│   └── Define los archivos y carpetas que Git no debe versionar.
│
└── .env.example
    └── Plantilla de las variables de entorno necesarias para ejecutar la aplicación.
>>>>>>> abd81c9 (actualización readme y estructura)
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
Estudiante de Ingeniería de Sistemas, Pontificia Universidad Javeriana  
GitHub: https://github.com/isabelsgp

**Juan Diego Arevalo**  
Estudiante de Ingeniería de Sistemas, Pontificia Universidad Javeriana  
GitHub: https://github.com/Juan123839

**Juan Pablo Vanegas**  
Estudiante de Ingeniería de Sistemas, Pontificia Universidad Javeriana  
GitHub: https://github.com/ujuanpvanegasvelandia02-ship-it

**David Vallejo**  
Estudiante de Ingeniería de Sistemas, Pontificia Universidad Javeriana  
GitHub: https://github.com/David-wallpaper

**Oscar Martinez Mantilla**  
Estudiante de Ingeniería de Sistemas, Pontificia Universidad Javeriana  
GitHub: https://github.com/martinezm-oe


--- 

## Licencia
Proyecto desarrollado con fines académicos.

---
