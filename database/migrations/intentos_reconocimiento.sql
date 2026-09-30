BEGIN;

-- Intentos realizados durante las sesiones de reconocimiento visual
CREATE TABLE intentos_reconocimiento (
    id_intento BIGINT GENERATED ALWAYS AS IDENTITY,
    id_usuario BIGINT NOT NULL,
    id_sesion BIGINT NOT NULL,
    id_letra BIGINT NOT NULL,
    es_correcto BOOLEAN NOT NULL,
    fecha_intento TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_intentos_reconocimiento
        PRIMARY KEY (id_intento),

    CONSTRAINT fk_intentos_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id_usuario)
        ON DELETE CASCADE,

    CONSTRAINT fk_intentos_sesion
        FOREIGN KEY (id_sesion)
        REFERENCES sesiones_reconocimiento(id_sesion)
        ON DELETE CASCADE,

    CONSTRAINT fk_intentos_letra
        FOREIGN KEY (id_letra)
        REFERENCES letras(id_letra)
        ON DELETE RESTRICT
);

-- Permite consultar los intentos realizados por usuario y fecha
CREATE INDEX idx_intentos_usuario_fecha
    ON intentos_reconocimiento (id_usuario, fecha_intento DESC);

COMMIT;