BEGIN;

-- Relaciona cada intento con el resultado que lo originó.
ALTER TABLE intentos_reconocimiento
    ADD COLUMN id_resultado BIGINT NOT NULL;

ALTER TABLE intentos_reconocimiento
    ADD CONSTRAINT fk_intentos_resultado
        FOREIGN KEY (id_resultado)
        REFERENCES resultados_reconocimiento(id_resultado)
        ON DELETE CASCADE;

-- Un mismo resultado puede generar como máximo un intento.
ALTER TABLE intentos_reconocimiento
    ADD CONSTRAINT uq_intentos_resultado
        UNIQUE (id_resultado);

COMMIT;