# src/dependencies/workspace.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.auth import get_current_user
from src.dependencies.repository import get_workspace_repository
from src.models.user import User
from src.models.workspace import Workspace
from src.repositories.workspace import WorkspaceRepository


async def get_current_workspace(
    workspace_id: int,  # we will get this from header/path/query later
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Workspace:
    """
    Dependency: load current workspace and verify current user is a member.
    Later: workspace_id will come from header (X-Workspace-ID) or path.
    """
    workspace = await workspace_repo.get_by_id(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    # Check membership
    membership = await workspace_repo.get_membership(current_user.id, workspace.id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )

    return workspace


async def require_admin(
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
):
    """
    Dependency guard: fail if current user is not admin in this workspace.
    """
    membership = await workspace_repo.get_membership(current_user.id, workspace.id)
    if not membership or membership.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    # No return value — just raises if not admin