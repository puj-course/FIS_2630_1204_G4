# Guía de trabajo con Git y GitHub

## Objetivo

Esta guía define el proceso que debe seguir el equipo para crear ramas, registrar cambios, actualizar el trabajo y generar Pull Requests sin afectar el código de otros integrantes.

## Flujo de ramas

El repositorio utiliza el siguiente flujo:

```text
rama individual o rama de tarea específica → develop → main
```

| Rama               | Uso                                                                                                      |
| ------------------ | -------------------------------------------------------------------------------------------------------- |
| `main`             | Contiene la versión estable. Está protegida y solo recibe cambios mediante Pull Request desde `develop`. |
| `develop`          | Integra el trabajo realizado durante el desarrollo.                                                      |
| Ramas individuales o de tareas | Contienen los cambios de una funcionalidad, corrección, prueba o documento específico.                   |

No se deben realizar pushes directos a `main`.

## Convenciones para nombres de ramas

Las ramas deben utilizar letras minúsculas, palabras separadas por guiones y un nombre relacionado con el cambio.

| Tipo       | Uso                                | Ejemplo                         |
| ---------- | ---------------------------------- | ------------------------------- |
| `feature/` | Nueva funcionalidad                | `feature/registro-usuarios`     |
| `fix/`     | Corrección de un error             | `fix/error-consulta-perfil`     |
| `docs/`    | Documentación                      | `docs/flujo-trabajo-git`        |
| `test/`    | Creación o modificación de pruebas | `test/flujo-perfil`             |
| `chore/`   | Configuración o dependencias       | `chore/actualizar-dependencias` |

No se deben utilizar espacios, tildes, nombres personales ni descripciones generales como `cambios`, `prueba` o `rama-nueva`.

## Crear una rama de trabajo

Antes de comenzar una tarea, se debe actualizar `develop`:

```bash
git switch develop
git pull
```

Después se crea una rama para la funcionalidad si es necesario:

```bash
git switch -c feature/nombre-del-cambio
```

Para confirmar la rama actual:

```bash
git branch --show-current
```

Cada rama debe atender una sola tarea o subissue.

## Registrar los cambios

Antes de crear un commit se deben revisar los archivos modificados:

```bash
git status
git diff
```

Se deben agregar únicamente los archivos relacionados con la tarea:

```bash
git add ruta/del/archivo
```
Si se quier agregar todos los cambios realizados:

```bash
git add .
```
Luego se revisa el contenido preparado:

```bash
git status
```

El commit debe seguir el formato:

```text
:emoji: tipo(módulo): descripción breve
```

Ejemplos:

```bash
git commit -m ":sparkles: feat(perfil): mostrar progreso del usuario"
git commit -m ":bug: fix(registro): corregir validación del correo"
git commit -m ":memo: docs(git): documentar flujo de trabajo"
git commit -m ":white_check_mark: test(perfil): agregar pruebas del endpoint"
git commit -m ":wrench: chore(deps): actualizar dependencias"
```

Finalmente se publica la rama:

```bash
git push -u origin nombre-de-la-rama
```

## Actualizar una rama individual

Las ramas individuales deben actualizarse con un Pull Request a develop

Si aparecen conflictos, se deben revisarse en github el PR para decidir que cambios permanecen.

## Crear un Pull Request hacia develop

Cuando la rama individual esté lista, se crea un Pull Request con:

```text
base: develop
compare: nombre-de-la-rama
```

El Pull Request debe incluir:

* Una descripción clara del cambio.
* La subissue relacionada.
* Los archivos principales modificados.
* Las pruebas ejecutadas.
* Evidencia cuando sea necesaria.
* Una solicitud de revisión a otro integrante.

No se deben crear Pull Requests desde ramas individuales directamente hacia `main`.

## Revisar un Pull Request

Antes de aprobar un Pull Request se debe comprobar:

* Que la rama base sea la correcta.
* Que los cambios correspondan únicamente a la tarea.
* Que no existan archivos eliminados accidentalmente.
* Que no se incluyan archivos como `.env`, `.venv`, `node_modules` o `dist`.
* Que las pruebas finalicen correctamente.
* Que los comentarios de revisión estén resueltos.

En **Files changed**, los archivos marcados como `Deleted` serán eliminados al fusionar el Pull Request.

## Integrar develop con main

Cuando los cambios de `develop` estén completos y probados, se crea un Pull Request con:

```text
base: main
compare: develop
```

La rama `main` está protegida, por lo que no permite pushes directos. El Pull Request debe ser revisado y aprobado antes del merge.

Antes de aprobarlo se deben revisar las diferencias:

```bash
git fetch origin
git diff --name-status origin/main...origin/develop
```

Una línea que comienza con `D` representa un archivo que será eliminado de `main`.

Después de integrar los cambios, `develop` puede sincronizarse nuevamente:

```bash
git switch develop
git pull
```

## Recomendaciones para evitar conflictos

* Actualizar `develop` antes de crear una rama.
* Crear una rama diferente para cada tarea si es necesario.
* Mantener los cambios pequeños y relacionados.
* Avisar cuando varias personas necesiten modificar el mismo archivo.
* Revisar `git status` antes de cada commit y push.
* Agregar archivos específicos en lugar de incluir cambios desconocidos.
* No utilizar `git push --force` en ramas compartidas.
* No modificar directamente `main`.
* No ejecutar comandos de restauración o eliminación sin revisar primero su efecto.
* No resolver conflictos eliminando automáticamente el trabajo de otro integrante.

## Resumen
1. Actualizar develop
2. Crear una rama individual
3. Realizar y revisar los cambios
4. Crear commits claros
5. Publicar la rama
6. Abrir un Pull Request hacia develop
7. Revisar y probar el Pull Request
8. Integrar develop en main mediante otro Pull Request

