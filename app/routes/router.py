from fastapi import APIRouter

from app.routes.autenticacion import router as autenticacion_router
from app.routes.letras import router as letras_router
from app.routes.perfil import router as perfil_router
from app.routes.progreso import router as progreso_router
from app.routes.resultados import router as resultados_router
from app.routes.resultados_reconocimiento import (
    router as resultados_reconocimiento_router,
)
from app.routes.sesiones import router as sesiones_router
from app.routes.usuarios import router as usuarios_router
from app.routes.vision import router as vision_router

api_router = APIRouter()

api_router.include_router(letras_router)
api_router.include_router(autenticacion_router)
api_router.include_router(usuarios_router)
api_router.include_router(perfil_router)
api_router.include_router(vision_router)
api_router.include_router(resultados_reconocimiento_router)
api_router.include_router(progreso_router)
api_router.include_router(resultados_router)
api_router.include_router(sesiones_router)