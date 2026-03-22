# src/dependencies/workspace.py
from typing import Annotated

from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.auth import get_current_user
from src.database import get_db
from src.models.user import User
from src.models.workspace import Workspace
from src.models.membership import Role
from src.repositories.workspace import WorkspaceRepository


# 🔹 Repository factory (OUTSIDE, top-level)
def get_workspace_repository(
    session: Annotated[AsyncSession, Depends(get_db)]
) -> WorkspaceRepository:
    return WorkspaceRepository(session=session)


# 🔹 Get current workspace
async def get_current_workspace(
    workspace_id: int,  # ← plain int, no Header or Path
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
) -> Workspace:

    workspace = await workspace_repo.get_by_id(workspace_id)
    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    membership = await workspace_repo.get_membership(current_user.id, workspace.id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this workspace",
        )

    return workspace


# 🔹 Admin guard
async def require_admin(
    workspace: Workspace = Depends(get_current_workspace),
    current_user: User = Depends(get_current_user),
    workspace_repo: WorkspaceRepository = Depends(get_workspace_repository),
):
    membership = await workspace_repo.get_membership(current_user.id, workspace.id)

    if not membership or membership.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )