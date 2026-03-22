
from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.membership import Membership
from src.models.workspace import Workspace


class WorkspaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, workspace_id: int) -> Optional[Workspace]:
        stmt = select(Workspace).where(Workspace.id == workspace_id, Workspace.deleted == False)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_membership(self, user_id: int, workspace_id: int) -> Optional[Membership]:
        stmt = select(Membership).where(
            Membership.user_id == user_id,
            Membership.workspace_id == workspace_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    

    async def get_all_for_user(self, user_id: int) -> List[Workspace]:
        """Get all workspaces where user is a member."""
        stmt = (
            select(Workspace)
            .join(Membership)
            .where(Membership.user_id == user_id, Workspace.deleted == False)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, name: str, description: str | None, creator_id: int) -> Workspace:
        workspace = Workspace(name=name, description=description)
        self.session.add(workspace)
        await self.session.flush()
        return workspace

    async def add_membership(self, user_id: int, workspace_id: int, role: str = "member"):
        membership = Membership(
            user_id=user_id,
            workspace_id=workspace_id,
            role=role,
        )
        self.session.add(membership)
        await self.session.flush()

    async def delete(self, workspace_id: int):
        stmt = delete(Workspace).where(Workspace.id == workspace_id)
        await self.session.execute(stmt)
        await self.session.commit()   