BEGIN;

-- Usuarios registrados en SignIA
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario BIGINT GENERATED ALWAYS AS IDENTITY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    contrasena_hash TEXT NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'usuario',
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_usuarios PRIMARY KEY (id_usuario),
    CONSTRAINT uq_usuarios_correo UNIQUE (correo),
    CONSTRAINT chk_usuarios_rol
        CHECK (rol IN ('usuario', 'administrador'))
);

-- Letras disponibles en el alfabeto LSC
CREATE TABLE IF NOT EXISTS letras (
    id_letra BIGINT GENERATED ALWAYS AS IDENTITY,
    letra VARCHAR(2) NOT NULL,
    descripcion TEXT,
    ruta_imagen TEXT,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    creada_por BIGINT,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_letras PRIMARY KEY (id_letra),
    CONSTRAINT uq_letras_letra UNIQUE (letra),
    CONSTRAINT fk_letras_usuario
        FOREIGN KEY (creada_por)
        REFERENCES usuarios(id_usuario)
        ON DELETE SET NULL
);

-- Sesiones iniciadas por los usuarios para practicar
CREATE TABLE IF NOT EXISTS sesiones_reconocimiento (
    id_sesion BIGINT GENERATED ALWAYS AS IDENTITY,
    id_usuario BIGINT NOT NULL,
    fecha_inicio TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP WITH TIME ZONE,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',

    CONSTRAINT pk_sesiones_reconocimiento PRIMARY KEY (id_sesion),
    CONSTRAINT fk_sesiones_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,
    CONSTRAINT chk_sesiones_estado
        CHECK (estado IN ('activa', 'finalizada', 'cancelada')),
    CONSTRAINT chk_sesiones_fechas
        CHECK (fecha_fin IS NULL OR fecha_fin >= fecha_inicio)
);

-- Resultados generados durante cada sesión
CREATE TABLE IF NOT EXISTS resultados_reconocimiento (
    id_resultado BIGINT GENERATED ALWAYS AS IDENTITY,
    id_sesion BIGINT NOT NULL,
    id_letra_objetivo BIGINT NOT NULL,
    id_letra_detectada BIGINT NOT NULL,
    confianza NUMERIC(5,4) NOT NULL,
    es_correcto BOOLEAN NOT NULL,
    fecha_resultado TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_resultados_reconocimiento PRIMARY KEY (id_resultado),
    CONSTRAINT fk_resultados_sesion
        FOREIGN KEY (id_sesion)
        REFERENCES sesiones_reconocimiento(id_sesion)
        ON DELETE CASCADE,
    CONSTRAINT fk_resultados_letra_objetivo
        FOREIGN KEY (id_letra_objetivo)
        REFERENCES letras(id_letra)
        ON DELETE RESTRICT,
    CONSTRAINT fk_resultados_letra_detectada
        FOREIGN KEY (id_letra_detectada)
        REFERENCES letras(id_letra)
        ON DELETE RESTRICT,
    CONSTRAINT chk_resultados_confianza
        CHECK (confianza >= 0 AND confianza <= 1),
    CONSTRAINT chk_resultados_coherencia
        CHECK (es_correcto = (id_letra_objetivo = id_letra_detectada))
);

-- Progreso de cada usuario para cada letra
CREATE TABLE IF NOT EXISTS progreso_usuario (
    id_progreso BIGINT GENERATED ALWAYS AS IDENTITY,
    id_usuario BIGINT NOT NULL,
    id_letra BIGINT NOT NULL,
    cantidad_intentos INTEGER NOT NULL DEFAULT 0,
    cantidad_aciertos INTEGER NOT NULL DEFAULT 0,
    dominada BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_ultima_practica TIMESTAMP WITH TIME ZONE,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_progreso_usuario PRIMARY KEY (id_progreso),
    CONSTRAINT uq_progreso_usuario_letra
        UNIQUE (id_usuario, id_letra),
    CONSTRAINT fk_progreso_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,
    CONSTRAINT fk_progreso_letra
        FOREIGN KEY (id_letra)
        REFERENCES letras(id_letra)
        ON DELETE RESTRICT,
    CONSTRAINT chk_progreso_intentos
        CHECK (cantidad_intentos >= 0),
    CONSTRAINT chk_progreso_aciertos
        CHECK (
            cantidad_aciertos >= 0
            AND cantidad_aciertos <= cantidad_intentos
        )
);

COMMIT;