from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application
from app.schemas.application import ApplicationCreate


async def create_application(
    db: AsyncSession,
    data: ApplicationCreate,
) -> Application:
    application = Application(
        vacancy_id=data.vacancy_id,
        notes=data.notes,
    )

    db.add(application)
    await db.commit()
    await db.refresh(application)

    return application


async def get_applications(
    db: AsyncSession,
) -> list[Application]:
    statement = (
        select(Application)
        .order_by(Application.created_at.desc())
    )

    result = await db.scalars(statement)

    return list(result.all())


async def get_application_by_id(
    db: AsyncSession,
    application_id: int,
) -> Application | None:
    return await db.get(
        Application,
        application_id,
    )


async def update_application_status(
    db: AsyncSession,
    application: Application,
    new_status,
) -> Application:
    application.status = new_status

    await db.commit()
    await db.refresh(application)

    return application