
from typing import Optional

from sqlalchemy import select
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