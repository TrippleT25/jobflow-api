from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.dashboard import get_dashboard_stats


async def get_dashboard_stats_service(
    db: AsyncSession,
    owner_id: int,
):
    return await get_dashboard_stats(
        db=db,
        owner_id=owner_id,
    )
