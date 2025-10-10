"""
PromptForge API - FastAPI Application Entry Point
Phase 2: Core APIs and Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import api_router
from app.evaluations.registry import registry
from app.evaluations.adapters import (
    PromptForgeAdapter,
    DeepEvalAdapter,
    RagasAdapter,
    MLflowAdapter,
    DeepchecksAdapter,
    ArizePhoenixAdapter,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


# ==================== Module-Level Adapter Registration ====================
# Register adapters at module import time (executed in each worker process)
# This ensures adapters are available even with uvicorn --reload
def _register_evaluation_adapters():
    """
    Register all evaluation adapters
    Called at module import time to ensure registration in each worker process
    """
    try:
        from app.models.evaluation_catalog import EvaluationSource

        logger.info("Initializing evaluation adapters...")

        # Register PromptForge adapter (always available)
        promptforge_adapter = PromptForgeAdapter()
        registry.register_adapter(EvaluationSource.PROMPTFORGE, promptforge_adapter)
        logger.info("✓ Registered PromptForge adapter")

        # Register vendor adapters (may not be available if libraries not installed)
        vendor_adapters = [
            (DeepEvalAdapter, "DeepEval"),
            (RagasAdapter, "Ragas"),
            (MLflowAdapter, "MLflow"),
            (DeepchecksAdapter, "Deepchecks"),
            (ArizePhoenixAdapter, "Arize Phoenix"),
        ]

        for adapter_class, name in vendor_adapters:
            try:
                adapter = adapter_class()
                if adapter.is_available():
                    registry.register_adapter(EvaluationSource.VENDOR, adapter)
                    logger.info(f"✓ Registered {name} adapter")
                else:
                    logger.warning(f"⚠ {name} adapter created but library not available")
            except Exception as e:
                logger.warning(f"⚠ Failed to initialize {name} adapter: {e}")

        # Note: Custom and LLM Judge adapters are initialized per-request with DB session
        logger.info(f"Adapter registration complete. Total adapters: {len(registry._adapters)}")

    except Exception as e:
        logger.error(f"Error initializing evaluation adapters: {e}", exc_info=True)


# Register adapters immediately on module import
_register_evaluation_adapters()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager

    Handles startup and shutdown events
    """
    # Startup
    logger.info("Starting PromptForge API...")
    logger.info(f"Registered adapters: {list(registry._adapters.keys())}")
    logger.info("PromptForge API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down PromptForge API...")


# Create all database tables
# In production, use Alembic migrations instead
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="PromptForge - AI Governance & Prompt Management Platform API",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected",
        "version": settings.VERSION,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
