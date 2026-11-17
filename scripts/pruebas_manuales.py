
import httpx

URL = "http://localhost:8000"


# Prueba 1: comprobar que el backend funciona
def probar_backend():
    respuesta = httpx.get(URL + "/health")

    print("\nPRUEBA 1: Estado del backend")
    print("Código HTTP:", respuesta.status_code)

    if respuesta.status_code == 200:
        print("Resultado: correcto, el backend responde")
    else:
        print("Resultado: el backend no respondió correctamente")


# Prueba 2: consultar las letras registradas
def probar_letras():
    respuesta = httpx.get(URL + "/letras")

    print("\nPRUEBA 2: Consultar alfabeto")
    print("Código HTTP:", respuesta.status_code)

    if respuesta.status_code == 200:
        print("Resultado: consulta realizada correctamente")
        print("Letras obtenidas:", respuesta.json())
    else:
        print("Resultado: no se pudieron consultar las letras")


# Prueba 3: comprobar el acceso protegido al perfil
def probar_perfil_sin_token():
    respuesta = httpx.get(URL + "/perfil")

    print("\nPRUEBA 3: Acceso al perfil sin iniciar sesión")
    print("Código HTTP:", respuesta.status_code)

    if respuesta.status_code in (401, 403):
        print("Resultado: correcto, acceso rechazado")
    else:
        print("Resultado: revisar la seguridad del perfil")


# Ejecutar las tres pruebas
probar_backend()
probar_letras()
probar_perfil_sin_token()
