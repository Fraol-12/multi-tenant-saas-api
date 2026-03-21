
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from src.core.security import get_current_user
from src.dependencies.workspace import get_current_workspace, require_admin
from src.models.user import User
from src.models.workspace import Workspace
from src.repositories.workspace import WorkspaceRepository
from src.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceRead,
    WorkspaceUpdate,
)
from src.dependencies.repository import get_workspace_repository

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("/", response_model=List[WorkspaceRead])
async def list_my_workspaces(
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
):
    """List all workspaces the current user is a member of."""
    workspaces = await workspace_repo.get_all_for_user(current_user.id)
    return workspaces


@router.post("/", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    workspace_in: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
):
    """Create a new workspace and make current user Admin."""
    workspace = await workspace_repo.create(
        name=workspace_in.name,
        description=workspace_in.description,
        creator_id=current_user.id,
    )
    await workspace_repo.session.flush()  # get ID

    # Auto-add creator as Admin
    await workspace_repo.add_membership(
        user_id=current_user.id,
        workspace_id=workspace.id,
        role="admin",
    )

    return workspace


@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    workspace: Workspace = Depends(get_current_workspace),
):
    """Get details of a specific workspace (must be member)."""
    return workspace


@router.patch("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(
    workspace_in: WorkspaceUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    require_admin_dep = Depends(require_admin),  # just for RBAC check
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
):
    """Update workspace name/description (admin only)."""
    if workspace_in.name is not None:
        workspace.name = workspace_in.name
    if workspace_in.description is not None:
        workspace.description = workspace_in.description

    await workspace_repo.session.flush()
    return workspace


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace: Workspace = Depends(get_current_workspace),
    require_admin_dep = Depends(require_admin),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
):
    """Delete workspace (admin only) – hard delete + cascade."""
    await workspace_repo.delete(workspace.id)
    # No return – 204 No Content