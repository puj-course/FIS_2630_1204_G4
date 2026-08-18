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

FIS_2630_1204_G4/
│
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── Plantillas utilizadas para estandarizar la creación de Issues.
│   └── workflows/
│       └── Flujos de automatización e integración continua del proyecto.
│
├── assets/
│   ├── diagrams/
│   │   └── Diagramas generales utilizados en la documentación.
│   ├── images/
│   │   └── Imágenes y recursos gráficos del proyecto.
│   └── logo/
│       └── Logo e identidad visual de SignIA.
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── Define las rutas y endpoints de la API.
│   │   ├── core/
│   │   │   └── Contiene la configuración general y aspectos de seguridad.
│   │   ├── database/
│   │   │   └── Gestiona la conexión entre FastAPI y PostgreSQL.
│   │   ├── models/
│   │   │   └── Define los modelos de datos del sistema.
│   │   ├── schemas/
│   │   │   └── Define los esquemas utilizados para validar datos.
│   │   ├── services/
│   │   │   └── Contiene la lógica de negocio de la aplicación.
│   │   ├── utils/
│   │   │   └── Funciones auxiliares reutilizables.
│   │   └── vision/
│   │       └── Contiene la lógica de visión por computador con OpenCV y MediaPipe.
│   └── tests/
│       └── Pruebas unitarias y de integración del backend.
│
├── database/
│   ├── diagrams/
│   │   └── Diagramas relacionados con el modelo de datos.
│   └── migrations/
│       └── Cambios y versiones de la estructura de la base de datos.
│
├── docs/
│   ├── api/
│   │   └── Documentación relacionada con los endpoints de la API.
│   ├── architecture/
│   │   └── Documentación de la arquitectura del sistema.
│   ├── database/
│   │   └── Diseño y documentación de la base de datos.
│   ├── requirements/
│   │   └── Requerimientos funcionales y no funcionales.
│   ├── scrum/
│   │   └── Documentación relacionada con Sprints y gestión Scrum.
│   └── user-guide/
│       └── Guías de uso de la plataforma.
│
├── frontend/
│   ├── public/
│   │   └── Archivos públicos utilizados por la aplicación web.
│   └── src/
│       ├── assets/
│       │   └── Recursos gráficos utilizados directamente por React.
│       ├── components/
│       │   └── Componentes reutilizables de la interfaz.
│       ├── pages/
│       │   └── Vistas principales de la plataforma.
│       ├── services/
│       │   └── Comunicación entre el frontend y la API.
│       └── utils/
│           └── Funciones auxiliares utilizadas en el frontend.
│
├── scripts/
│   └── Scripts utilizados para automatizar tareas del proyecto.
│
├── temp/
│   └── uploads/
│       └── Archivos temporales generados durante la ejecución.
│
├── .env.example
│   └── Plantilla de las variables de entorno necesarias.
│
├── .gitignore
│   └── Define archivos y carpetas que Git no debe versionar.
│
├── BOILERPLATE_template.md
│   └── Plantilla base utilizada como referencia para organizar el repositorio.
│
├── CONTRIBUTING.md
│   └── Normas y recomendaciones para contribuir al proyecto.
│
├── LICENSE
│   └── Licencia bajo la cual se encuentra el proyecto.
│
└── README.md
    └── Documento principal con la descripción, tecnologías, instalación y estructura de SignIA.
```

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
