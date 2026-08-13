# Plantilla del README del proyecto 2610

# Nombre de la Aplicación

## Descripción
Breve descripción del sistema de software, el problema que busca solucionar y el contexto general del proyecto.

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
- **Frontend:** JavaFX
- **Backend:** Java – Spring Boot
- **Base de Datos:** PostgreSQL
- **IA / Data Science:** Python, Pandas, Scikit-learn
- **DevOps:** GitHub Actions, Docker, SonarQube
- **Control de versiones:** Git

---

## Estructura del Proyecto
```text
project-name/
├── app/
│   ├── index.js
│   │   └── Punto de entrada principal de la aplicación.
│   ├── package.json
│   │   └── Define las dependencias, scripts y configuración del proyecto.
│   ├── routes/
│   │   ├── index.js
│   │   └── Define las rutas o endpoints principales de la aplicación.
│   ├── controllers/
│   │   ├── userController.js
│   │   └── Contiene la lógica encargada de procesar las solicitudes.
│   └── services/
│       ├── userService.js
│       └── Contiene la lógica de negocio y servicios reutilizables.
│
├── conf/
│   ├── config.json
│   │   └── Contiene parámetros generales de configuración.
│   ├── database.js
│   │   └── Configura la conexión con la base de datos.
│   └── environment.example
│       └── Ejemplo de las variables de entorno necesarias para ejecutar el proyecto.
│
├── docs/
│   ├── architecture.md
│   │   └── Describe la arquitectura general del sistema.
│   ├── api.md
│   │   └── Documenta los endpoints, parámetros y respuestas de la API.
│   ├── installation.md
│   │   └── Explica cómo instalar y configurar el proyecto.
│   └── user_guide.md
│       └── Guía básica para el uso de la aplicación.
│
├── scripts/
│   ├── setup.sh
│   │   └── Automatiza la instalación y configuración inicial del proyecto.
│   ├── start.sh
│   │   └── Permite iniciar la aplicación.
│   ├── test.sh
│   │   └── Ejecuta las pruebas automatizadas.
│   └── deploy.sh
│       └── Automatiza tareas relacionadas con el despliegue.
│
├── src/
│   ├── models/
│   │   ├── user.js
│   │   └── Define las estructuras o modelos de datos del sistema.
│   ├── utils/
│   │   ├── helpers.js
│   │   └── Contiene funciones auxiliares reutilizables.
│   ├── middleware/
│   │   ├── auth.js
│   │   └── Contiene funciones que se ejecutan antes o después de una solicitud.
│   └── tests/
│       ├── user.test.js
│       └── Contiene pruebas unitarias o de integración del proyecto.
│
├── temp/
│   ├── .gitkeep
│   │   └── Permite conservar la carpeta vacía dentro del repositorio.
│   ├── example.tmp
│   │   └── Ejemplo de archivo temporal generado durante la ejecución.
│   └── uploads/
│       └── Carpeta destinada a almacenar archivos temporales cargados por usuarios.
│
├── BOILERPLATE_template.md
│   └── Documento que explica la estructura base y cómo utilizar este boilerplate.
│
├── CONTRIBUTING.md
│   └── Define las normas y recomendaciones para contribuir al proyecto.
│
├── LICENSE
│   └── Especifica la licencia bajo la cual se distribuye el proyecto.
│
├── README.md
│   └── Documento principal con la descripción, instalación, uso y características del proyecto.
│
├── .gitignore
│   └── Define los archivos y carpetas que Git no debe versionar.
│
└── .env.example
    └── Plantilla de las variables de entorno necesarias para ejecutar la aplicación.
```

---

## Instalación y Ejecución
**Requisitos**
- Docker y Docker Compose
- Git
- Java 17+
- Python 3.10+

## Clonar el repositorio
```text
git clone https://github.com/organizacion/proyecto.git
cd proyecto
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

**Estudiante 1**  
Estudiante de Ciencia de Datos, Pontificia Universidad Javeriana  
📧 est1.u@javeriana.edu.co  

**Estudiante 2**  
Estudiante de Ingeniería en Sistemas, Pontificia Universidad Javeriana  
📧 est2@javeriana.edu.co

**Estudiante 3**  
Estudiante de Ingeniería en Sistemas, Pontificia Universidad Javeriana  
📧 vallejo-david@javeriana.edu.co 
--- 

## Licencia
Proyecto desarrollado con fines académicos.
