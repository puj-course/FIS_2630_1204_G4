import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.limiter import limiter
from app.routes.router import api_router
from app.services.vision_service import cerrar_detectores
from conf.logging_config import configurar_logging

configurar_logging()

logger = logging.getLogger(__name__)

ORIGENES_PERMITIDOS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        cerrar_detectores()


app = FastAPI(
    title="SignIA API",
    description="Backend para la plataforma de aprendizaje del alfabeto LSC",
    version="1.0.1",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)


@app.exception_handler(Exception)
async def manejador_errores_no_controlados(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Error no controlado en %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "Ocurrió un error interno, Intenta más tarde."},
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/assets",
    StaticFiles(directory="app/assets"),
    name="assets",
)

app.include_router(api_router)


@app.get("/health", tags=["Estado"])
def comprobar_estado():
    return {
        "estado": "ok",
        "mensaje": "El backend de SignIA está funcionando",
    }