# HU#4 - Consultar Alfabeto - Diagrama de Componentes

```plantuml
@startuml
' skinparam linetype ortho
!include https://static.visual-paradigm.com/web/resources/plantuml-stdlib/themes/vp.puml
skinparam vpDiagramType ComponentDiagram
left to right direction

title HU#4 - Consultar Alfabeto - Diagrama de Componentes

/'
Visión Arquitectónica
El cliente consulta la pantalla de aprendizaje; la capa de presentación pide
el alfabeto al módulo de letras, que lo obtiene de la tabla letras. La
actualización de una letra (PATCH) requiere además validar el token con el
módulo de autenticación.
'/

package "Capa Cliente" {
  component "Cliente Navegador Web" as Browser
}

package "Capa de Presentación" {
  component "Módulo Aprender" as AprenderFrontend
}

package "Capa de Aplicación" {
  component "Módulo Letras" as LetrasModule
  component "Módulo Autenticación" as AuthModule
}

package "Capa de Datos" {
  component "Tabla letras" as LetrasStore
}

' Declaración de Interfaces
interface "Interfaz Web" as iWebUI
interface "API de Letras" as iLetrasApi
interface "Validar Token" as iValidarToken
interface "API de Persistencia" as iPersistence

' Interfaces Provistas
iWebUI -- AprenderFrontend
iLetrasApi -- LetrasModule
iValidarToken -- AuthModule
iPersistence -- LetrasStore

' Interfaces Requeridas
Browser --( iWebUI
AprenderFrontend --( iLetrasApi
LetrasModule --( iValidarToken
LetrasModule --( iPersistence

@enduml
```
