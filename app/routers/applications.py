from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatusUpdate,
)
from app.services.applications import (
    create_application_service,
    get_application_service,
    get_applications_service,
    update_application_status_service,
)


router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
)


@router.post(
    "",
    response_model=ApplicationRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    data: ApplicationCreate,
    db: AsyncSession = Depends(get_db),
):
    return await create_application_service(
        db=db,
        data=data,
    )


@router.get(
    "",
    response_model=list[ApplicationRead],
)
async def get_applications(
    db: AsyncSession = Depends(get_db),
):
    return await get_applications_service(db)


@router.get(
    "/{application_id}",
    response_model=ApplicationRead,
)
async def get_application(
    application_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_application_service(
        db=db,
        application_id=application_id,
    )


@router.patch(
    "/{application_id}/status",
    response_model=ApplicationRead,
)
async def update_application_status(
    application_id: int,
    data: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
):
    return await update_application_status_service(
        db=db,
        application_id=application_id,
        data=data,
    )