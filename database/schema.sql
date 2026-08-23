BEGIN;

CREATE TABLE usuarios (
    id_usuario BIGINT GENERATED ALWAYS AS IDENTITY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL,
    contrasena_hash TEXT NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'usuario',
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_usuarios
        PRIMARY KEY (id_usuario),

    CONSTRAINT uq_usuarios_correo
        UNIQUE (correo),

    CONSTRAINT chk_usuarios_rol
        CHECK (rol IN ('usuario', 'administrador'))
);

CREATE TABLE letras (
    id_letra BIGINT GENERATED ALWAYS AS IDENTITY,
    letra VARCHAR(2) NOT NULL,
    descripcion TEXT,
    ruta_imagen TEXT,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    creada_por BIGINT,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_letras
        PRIMARY KEY (id_letra),

    CONSTRAINT uq_letras_letra
        UNIQUE (letra),

    CONSTRAINT fk_letras_usuario
        FOREIGN KEY (creada_por)
        REFERENCES usuarios(id_usuario)
        ON DELETE SET NULL
);

COMMIT;