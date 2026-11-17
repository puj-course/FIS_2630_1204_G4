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

-- Abecedario en Lengua de Señas Colombiana con sus imágenes
INSERT INTO letras (
    letra,
    descripcion,
    ruta_imagen
)
VALUES
    ('A', 'Seña de la letra A en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA A.jpg'),
    ('B', 'Seña de la letra B en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA B.jpg'),
    ('C', 'Seña de la letra C en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA C.jpg'),
    ('D', 'Seña de la letra D en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA D.jpg'),
    ('E', 'Seña de la letra E en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA E.jpg'),
    ('F', 'Seña de la letra F en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA F.jpg'),
    ('G', 'Seña de la letra G en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA G.jpg'),
    ('H', 'Seña de la letra H en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA H.jpg'),
    ('I', 'Seña de la letra I en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA I.jpg'),
    ('J', 'Seña de la letra J en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA J.jpg'),
    ('K', 'Seña de la letra K en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA K.jpg'),
    ('L', 'Seña de la letra L en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA L.jpg'),
    ('M', 'Seña de la letra M en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA M.jpg'),
    ('N', 'Seña de la letra N en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA N.jpg'),
    ('Ñ', 'Seña de la letra Ñ en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA Ñ.jpg'),
    ('O', 'Seña de la letra O en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA O.jpg'),
    ('P', 'Seña de la letra P en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA P.jpg'),
    ('Q', 'Seña de la letra Q en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA Q.jpg'),
    ('R', 'Seña de la letra R en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA R.jpg'),
    ('S', 'Seña de la letra S en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA S.jpg'),
    ('T', 'Seña de la letra T en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA T.jpg'),
    ('U', 'Seña de la letra U en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA U.jpg'),
    ('V', 'Seña de la letra V en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA V.jpg'),
    ('W', 'Seña de la letra W en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA W.jpg'),
    ('X', 'Seña de la letra X en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA X.jpg'),
    ('Y', 'Seña de la letra Y en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA Y.jpg'),
    ('Z', 'Seña de la letra Z en Lengua de Señas Colombiana.', '/assets/alfabeto/LETRA Z.jpg')

ON CONFLICT (letra) DO UPDATE SET
    descripcion = EXCLUDED.descripcion,
    ruta_imagen = EXCLUDED.ruta_imagen;


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


