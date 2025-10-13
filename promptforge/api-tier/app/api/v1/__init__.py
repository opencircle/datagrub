"""
API v1 router
"""
from fastapi import APIRouter
from app.api.v1 import auth, users, organizations, projects, prompts, evaluations, evaluation_catalog, traces, policies
from app.api.v1.endpoints import model_providers, playground, call_insights, models, insight_comparison

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(prompts.router, prefix="/prompts", tags=["prompts"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["evaluations"])
api_router.include_router(evaluation_catalog.router, prefix="/evaluation-catalog", tags=["evaluation-catalog"])
api_router.include_router(traces.router, prefix="/traces", tags=["traces"])
api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(models.router, prefix="/models", tags=["models"])
api_router.include_router(model_providers.router, prefix="/model-providers", tags=["model-providers"])
api_router.include_router(playground.router, prefix="/playground", tags=["playground"])
api_router.include_router(call_insights.router, prefix="/call-insights", tags=["call-insights"])
api_router.include_router(insight_comparison.router, prefix="/insights", tags=["insight-comparison"])
