from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.autenticacion import router as autenticacion_router
from app.routes.letras import router as letras_router
from app.routes.usuarios import router as usuarios_router
from app.routes.perfil import router as perfil_router

app = FastAPI(
    title="SignIA API",
    description="Backend para la plataforma de aprendizaje del alfabeto LSC",
    version="1.0.0"
)

origenes_permitidos = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_permitidos,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(letras_router)
app.include_router(autenticacion_router)
app.include_router(usuarios_router)
app.include_router(perfil_router)

@app.get("/health", tags=["Estado"])
def comprobar_estado():
    return {
        "estado": "ok",
        "mensaje": "El backend de SignIA está funcionando"
    }