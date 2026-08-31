BEGIN;

-- Usuarios de prueba
INSERT INTO usuarios (
    nombre,
    correo,
    contrasena_hash,
    rol
)
VALUES
    (
        'Usuario de prueba',
        'usuario.prueba@signia.local',
        'HASH_DE_PRUEBA_NO_UTILIZABLE',
        'usuario'
    ),
    (
        'Administrador de prueba',
        'admin.prueba@signia.local',
        'HASH_DE_PRUEBA_NO_UTILIZABLE',
        'administrador'
    )
ON CONFLICT (correo) DO NOTHING;

-- Letras de prueba
INSERT INTO letras (
    letra,
    descripcion,
    ruta_imagen,
    creada_por
)
SELECT
    datos.letra,
    datos.descripcion,
    datos.ruta_imagen,
    usuario.id_usuario
FROM usuarios AS usuario
CROSS JOIN (
    VALUES
        (
            'A',
            'Representación de prueba para la letra A.',
            'assets/alfabeto/a.png'
        ),
        (
            'B',
            'Representación de prueba para la letra B.',
            'assets/alfabeto/b.png'
        )
) AS datos(letra, descripcion, ruta_imagen)
WHERE usuario.correo = 'admin.prueba@signia.local'
ON CONFLICT (letra) DO NOTHING;

-- Sesión de reconocimiento de prueba
INSERT INTO sesiones_reconocimiento (
    id_usuario,
    fecha_inicio,
    fecha_fin,
    estado
)
SELECT
    usuario.id_usuario,
    TIMESTAMPTZ '2026-08-24 10:00:00-05',
    TIMESTAMPTZ '2026-08-24 10:10:00-05',
    'finalizada'
FROM usuarios AS usuario
WHERE usuario.correo = 'usuario.prueba@signia.local'
  AND NOT EXISTS (
      SELECT 1
      FROM sesiones_reconocimiento AS sesion
      WHERE sesion.id_usuario = usuario.id_usuario
        AND sesion.fecha_inicio =
            TIMESTAMPTZ '2026-08-24 10:00:00-05'
  );

-- Resultados de reconocimiento de prueba
INSERT INTO resultados_reconocimiento (
    id_sesion,
    id_letra_objetivo,
    id_letra_detectada,
    confianza,
    es_correcto,
    fecha_resultado
)
SELECT
    sesion.id_sesion,
    letra_objetivo.id_letra,
    letra_detectada.id_letra,
    datos.confianza,
    datos.es_correcto,
    datos.fecha_resultado
FROM sesiones_reconocimiento AS sesion
JOIN usuarios AS usuario
    ON usuario.id_usuario = sesion.id_usuario
CROSS JOIN (
    VALUES
        (
            'A',
            'A',
            0.9800,
            TRUE,
            TIMESTAMPTZ '2026-08-24 10:02:00-05'
        ),
        (
            'B',
            'A',
            0.7200,
            FALSE,
            TIMESTAMPTZ '2026-08-24 10:05:00-05'
        )
) AS datos(
    letra_objetivo,
    letra_detectada,
    confianza,
    es_correcto,
    fecha_resultado
)
JOIN letras AS letra_objetivo
    ON letra_objetivo.letra = datos.letra_objetivo
JOIN letras AS letra_detectada
    ON letra_detectada.letra = datos.letra_detectada
WHERE usuario.correo = 'usuario.prueba@signia.local'
  AND sesion.fecha_inicio =
      TIMESTAMPTZ '2026-08-24 10:00:00-05'
  AND NOT EXISTS (
      SELECT 1
      FROM resultados_reconocimiento AS resultado
      WHERE resultado.id_sesion = sesion.id_sesion
        AND resultado.fecha_resultado = datos.fecha_resultado
  );

-- Progreso de prueba
INSERT INTO progreso_usuario (
    id_usuario,
    id_letra,
    cantidad_intentos,
    cantidad_aciertos,
    dominada,
    fecha_ultima_practica
)
SELECT
    usuario.id_usuario,
    letra.id_letra,
    datos.cantidad_intentos,
    datos.cantidad_aciertos,
    datos.dominada,
    TIMESTAMPTZ '2026-08-24 10:05:00-05'
FROM usuarios AS usuario
CROSS JOIN (
    VALUES
        ('A', 1, 1, TRUE),
        ('B', 1, 0, FALSE)
) AS datos(
    letra,
    cantidad_intentos,
    cantidad_aciertos,
    dominada
)
JOIN letras AS letra
    ON letra.letra = datos.letra
WHERE usuario.correo = 'usuario.prueba@signia.local'
ON CONFLICT (id_usuario, id_letra)
DO UPDATE SET
    cantidad_intentos = EXCLUDED.cantidad_intentos,
    cantidad_aciertos = EXCLUDED.cantidad_aciertos,
    dominada = EXCLUDED.dominada,
    fecha_ultima_practica = EXCLUDED.fecha_ultima_practica,
    fecha_actualizacion = CURRENT_TIMESTAMP;

-- ESTE ARCHIVO ES NETAMENTE PARA PRUEBAS EN LA BASE DE DATOS, NO DEBE SER UTILIZADO EN EL PROYECTO.

COMMIT;


