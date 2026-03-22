# src/main.py
from fastapi import FastAPI, Depends 
from sqlalchemy import text 
from sqlalchemy.ext.asyncio import AsyncSession 

from src.config import settings
from src.database import get_db 

from src.dependencies.repository import get_user_repository
from src.repositories.user import UserRepository
from src.dependencies.auth import get_current_user
from src.models.user import User 
from src.api.v1.routers import auth
from src.api.v1.routers import auth, workspace


# We'll add more imports later (routers, middleware, exception handlers, etc.)

app = FastAPI(
    title=settings.project_name,
    description=(
        "Multi-tenant Task & Workspace Manager API\n\n"
        "Secure, workspace-isolated task management with role-based access."
    ),
    version="0.1.0",
    # Only expose docs in non-production environments
    docs_url="/docs" if settings.environment != "production" else None,
    redoc_url="/redoc" if settings.environment != "production" else None,
    openapi_url="/openapi.json" if settings.environment != "production" else None,
)


app.include_router(auth.router, prefix=settings.api_v1_str)

app.include_router(workspace.router, prefix=settings.api_v1_str)



@app.get("/health", summary="Health check endpoint")
async def health_check():
    """
    Simple health check to verify the API is running.
    Returns current environment for debugging.
    """
    return {
        "status": "healthy",
        "environment": settings.environment,
        "project": settings.project_name,
    }


# Optional: root endpoint redirecting to docs (common pattern)
@app.get("/", include_in_schema=False)
async def root():
    if settings.environment != "production":
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/docs")
    return {"message": "API is running"}


@app.get("/test-db", summary="Test database connection")
async def test_database(db: AsyncSession = Depends(get_db)):
    """
    Simple query to verify DB connectivity.
    Returns pong if everything is wired correctly.
    """
    result = await db.execute(text("SELECT 'pong' AS status"))
    return {"db_status": result.scalar_one()}

@app.get("/test-repo")
async def test_repository(repo: UserRepository = Depends(get_user_repository)):
    # Just to prove injection works — returns empty list for now
    return {"message": "Repository injected successfully"}

@app.get("/test-auth", response_model_exclude={"password_hash"})
async def test_auth(current_user: User = Depends(get_current_user)):
    return current_user 