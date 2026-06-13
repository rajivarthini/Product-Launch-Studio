from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.workflow import router as workflow_router
from app.core.logging import setup_logging
from app.core.config import settings

setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Product Launch Studio API",
        version="0.1.0",
        docs_url="/docs" if settings.ENV != "production" else None,
        redoc_url="/redoc" if settings.ENV != "production" else None,
        openapi_url="/openapi.json" if settings.ENV != "production" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(workflow_router, prefix="/api")

    import os
    from pathlib import Path
    from fastapi.staticfiles import StaticFiles
    
    upload_dir = Path(settings.LOCAL_UPLOAD_DIR).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    
    logger.info(f"Mounted static files at /uploads pointing to {upload_dir}")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        logger.error("Validation error for %s %s: %s", request.method, request.url, exc.errors())
        return JSONResponse(
            status_code=422,
            content={"detail": exc.errors(), "body": str(exc.body)},
        )

    return app


app = create_app()







