# Diagrama entidad-relación de SignIA

El siguiente diagrama representa la estructura inicial de la base de datos de SignIA y las relaciones implementadas mediante claves foráneas.

```mermaid
erDiagram
    USUARIOS {
        BIGINT id_usuario PK
        VARCHAR nombre
        VARCHAR correo UK
        TEXT contrasena_hash
        VARCHAR rol
        TIMESTAMPTZ fecha_creacion
    }

    LETRAS {
        BIGINT id_letra PK
        VARCHAR letra UK
        TEXT descripcion
        TEXT ruta_imagen
        BOOLEAN activa
        BIGINT creada_por FK
        TIMESTAMPTZ fecha_creacion
        TIMESTAMPTZ fecha_actualizacion
    }

    SESIONES_RECONOCIMIENTO {
        BIGINT id_sesion PK
        BIGINT id_usuario FK
        TIMESTAMPTZ fecha_inicio
        TIMESTAMPTZ fecha_fin
        VARCHAR estado
    }

    RESULTADOS_RECONOCIMIENTO {
        BIGINT id_resultado PK
        BIGINT id_sesion FK
        BIGINT id_letra_objetivo FK
        BIGINT id_letra_detectada FK
        NUMERIC confianza
        BOOLEAN es_correcto
        TIMESTAMPTZ fecha_resultado
    }

    PROGRESO_USUARIO {
        BIGINT id_progreso PK
        BIGINT id_usuario FK
        BIGINT id_letra FK
        INTEGER cantidad_intentos
        INTEGER cantidad_aciertos
        BOOLEAN dominada
        TIMESTAMPTZ fecha_ultima_practica
        TIMESTAMPTZ fecha_actualizacion
    }

    USUARIOS ||--o{ SESIONES_RECONOCIMIENTO : realiza
    USUARIOS ||--o{ PROGRESO_USUARIO : registra
    USUARIOS o|--o{ LETRAS : crea
    SESIONES_RECONOCIMIENTO ||--o{ RESULTADOS_RECONOCIMIENTO : contiene
    LETRAS ||--o{ PROGRESO_USUARIO : corresponde
    LETRAS ||--o{ RESULTADOS_RECONOCIMIENTO : objetivo
    LETRAS ||--o{ RESULTADOS_RECONOCIMIENTO : detectada