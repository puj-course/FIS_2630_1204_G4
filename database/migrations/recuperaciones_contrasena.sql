BEGIN;

-- Solicitudes para recuperar la cuenta sin guardar el token original
CREATE TABLE recuperaciones_contrasena (
    id_recuperacion BIGINT GENERATED ALWAYS AS IDENTITY,
    id_usuario BIGINT NOT NULL,
    token_hash VARCHAR(64) NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_expiracion TIMESTAMP WITH TIME ZONE NOT NULL,
    fecha_uso TIMESTAMP WITH TIME ZONE,
    fecha_invalidacion TIMESTAMP WITH TIME ZONE,

    CONSTRAINT pk_recuperaciones_contrasena
        PRIMARY KEY (id_recuperacion),
    CONSTRAINT uq_recuperaciones_token_hash
        UNIQUE (token_hash),
    CONSTRAINT fk_recuperaciones_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,
    CONSTRAINT chk_recuperaciones_token_hash
        CHECK (token_hash ~ '^[0-9a-f]{64}$'),
    CONSTRAINT chk_recuperaciones_expiracion
        CHECK (fecha_expiracion > fecha_creacion),
    CONSTRAINT chk_recuperaciones_uso
        CHECK (
            fecha_uso IS NULL
            OR (
                fecha_uso >= fecha_creacion
                AND fecha_uso < fecha_expiracion
            )
        ),
    CONSTRAINT chk_recuperaciones_invalidacion
        CHECK (
            fecha_invalidacion IS NULL
            OR fecha_invalidacion >= fecha_creacion
        ),
    CONSTRAINT chk_recuperaciones_estado
        CHECK (fecha_uso IS NULL OR fecha_invalidacion IS NULL)
);

-- Permite consultar las solicitudes recientes de cada usuario
CREATE INDEX idx_recuperaciones_usuario_fecha
    ON recuperaciones_contrasena (id_usuario, fecha_creacion DESC);

COMMIT;
