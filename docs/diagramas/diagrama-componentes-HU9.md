# HU#9 - Registrar Usuarios - Diagrama de Componentes

```plantuml
@startuml
' skinparam linetype ortho
!include https://static.visual-paradigm.com/web/resources/plantuml-stdlib/themes/vp.puml
skinparam vpDiagramType ComponentDiagram
left to right direction

title HU#9 - Registrar Usuarios - Diagrama de Componentes

/'
Visión Arquitectónica
El cliente usa el formulario de registro; la capa de presentación lo envía al
backend; el módulo de autenticación orquesta la creación y delega en el módulo
de usuarios, que persiste el registro en la base de datos.
'/

package "Capa Cliente" {
  component "Cliente Navegador Web" as Browser
}

package "Capa de Presentación" {
  component "Módulo Registro" as RegistroFrontend
}

package "Capa de Aplicación" {
  component "Módulo Autenticación" as AuthModule
  component "Módulo Usuarios" as UsuariosModule
}

package "Capa de Datos" {
  component "Tabla usuarios" as UsuariosStore
}

' Declaración de Interfaces
interface "Interfaz Web" as iWebUI
interface "API de Registro" as iRegistro
interface "Crear Usuario" as iCrearUsuario
interface "API de Persistencia" as iPersistence

' Interfaces Provistas
iWebUI -- RegistroFrontend
iRegistro -- AuthModule
iCrearUsuario -- UsuariosModule
iPersistence -- UsuariosStore

' Interfaces Requeridas
Browser --( iWebUI
RegistroFrontend --( iRegistro
AuthModule --( iCrearUsuario
UsuariosModule --( iPersistence

@enduml
```
