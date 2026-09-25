import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.routes.autenticacion import router as autenticacion_router
from app.routes.letras import router as letras_router
from app.routes.perfil import router as perfil_router
from app.routes.progreso import router as progreso_router
from app.routes.resultados import router as resultados_router
from app.routes.resultados_reconocimiento import (
    router as resultados_reconocimiento_router,
)
from app.routes.usuarios import router as usuarios_router
from app.routes.vision import router as vision_router
from app.services.vision_service import cerrar_detectores
from conf.logging_config import configurar_logging

configurar_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        # Libera los modelos al cerrar el backend
        cerrar_detectores()


app = FastAPI(
    title="SignIA API",
    description="Backend para la plataforma de aprendizaje del alfabeto LSC",
    version="1.0.0",
    lifespan=lifespan,
)

@app.exception_handler(Exception)
async def manejador_errores_no_controlados(request: Request, exc: Exception):
    logger.exception(
        "Error no controlado en %s %s", request.method, request.url.path
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno, Intenta más tarde."},
    )

app.mount(
    "/assets",
    StaticFiles(directory="app/assets"),
    name="assets"
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
app.include_router(vision_router)
app.include_router(resultados_reconocimiento_router)
app.include_router(progreso_router)
app.include_router(resultados_router)
@app.get("/health", tags=["Estado"])
def comprobar_estado():
    return {
        "estado": "ok",
        "mensaje": "El backend de SignIA está funcionando"
    }