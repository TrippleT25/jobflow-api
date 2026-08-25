from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import (
    Application,
    ApplicationStatus,
)
from app.repositories.applications import (
    create_application,
    get_application_by_id,
    get_applications,
    update_application_status,
)
from app.repositories.vacancies import get_vacancy_by_id
from app.schemas.application import (
    ApplicationCreate,
    ApplicationStatusUpdate,
)


ALLOWED_TRANSITIONS = {
    ApplicationStatus.NEW: {
        ApplicationStatus.APPLIED,
    },
    ApplicationStatus.APPLIED: {
        ApplicationStatus.HR_SCREEN,
        ApplicationStatus.REJECTED,
    },
    ApplicationStatus.HR_SCREEN: {
        ApplicationStatus.TECH_INTERVIEW,
        ApplicationStatus.REJECTED,
    },
    ApplicationStatus.TECH_INTERVIEW: {
        ApplicationStatus.FINAL_INTERVIEW,
        ApplicationStatus.OFFER,
        ApplicationStatus.REJECTED,
    },
    ApplicationStatus.FINAL_INTERVIEW: {
        ApplicationStatus.OFFER,
        ApplicationStatus.REJECTED,
    },
    ApplicationStatus.OFFER: set(),
    ApplicationStatus.REJECTED: set(),
}


async def create_application_service(
    db: AsyncSession,
    data: ApplicationCreate,
) -> Application:
    vacancy = await get_vacancy_by_id(
        db=db,
        vacancy_id=data.vacancy_id,
    )

    if vacancy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found",
        )

    return await create_application(
        db=db,
        data=data,
    )


async def get_applications_service(
    db: AsyncSession,
) -> list[Application]:
    return await get_applications(db)


async def get_application_service(
    db: AsyncSession,
    application_id: int,
) -> Application:
    application = await get_application_by_id(
        db=db,
        application_id=application_id,
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application


async def update_application_status_service(
    db: AsyncSession,
    application_id: int,
    data: ApplicationStatusUpdate,
) -> Application:
    application = await get_application_service(
        db=db,
        application_id=application_id,
    )

    allowed_statuses = ALLOWED_TRANSITIONS[
        application.status
    ]

    if data.status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Cannot change application status "
                f"from {application.status} to {data.status}"
            ),
        )

    return await update_application_status(
        db=db,
        application=application,
        new_status=data.status,
    )