# HU#10 - Consultar Perfil y Progreso - Diagrama de Componentes

```plantuml
@startuml
' skinparam linetype ortho
!include https://static.visual-paradigm.com/web/resources/plantuml-stdlib/themes/vp.puml
skinparam vpDiagramType ComponentDiagram
left to right direction

title HU#10 - Consultar Perfil y Progreso - Diagrama de Componentes

/'
Visión Arquitectónica
El cliente consulta su perfil; la capa de presentación pide el token al
módulo de autenticación y el perfil al módulo de perfil, que calcula el
porcentaje de progreso cruzando letras activas y avances del usuario.
'/

package "Capa Cliente" {
  component "Cliente Navegador Web" as Browser
}

package "Capa de Presentación" {
  component "Módulo Perfil" as PerfilFrontend
}

package "Capa de Aplicación" {
  component "Módulo Autenticación" as AuthModule
  component "Módulo Perfil" as PerfilModule
}

package "Capa de Datos" {
  component "Tabla usuarios" as UsuariosStore
  component "Tabla letras" as LetrasStore
  component "Tabla progreso_usuario" as ProgresoStore
}

' Declaración de Interfaces
interface "Interfaz Web" as iWebUI
interface "API de Perfil" as iPerfil
interface "Validar Token" as iValidarToken
interface "API de Usuarios" as iUsuarios
interface "API de Letras" as iLetras
interface "API de Progreso" as iProgreso

' Interfaces Provistas
iWebUI -- PerfilFrontend
iPerfil -- PerfilModule
iValidarToken -- AuthModule
iUsuarios -- UsuariosStore
iLetras -- LetrasStore
iProgreso -- ProgresoStore

' Interfaces Requeridas
Browser --( iWebUI
PerfilFrontend --( iPerfil
PerfilModule --( iValidarToken
AuthModule --( iUsuarios
PerfilModule --( iLetras
PerfilModule --( iProgreso

@enduml
```
