from arq.jobs import Job
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.queue import create_redis_pool
from app.routers.auth import get_current_user
from app.schemas.job import JobQueued, JobStatusResponse
from app.schemas.vacancy import (
    VacancyCreate,
    VacancyList,
    VacancyRead,
    VacancyUpdate,
)
from app.services.vacancies import (
    create_vacancy_service,
    delete_vacancy_service,
    get_vacancies_service,
    get_vacancy_service,
    update_vacancy_service,
)
from app.services.vacancies import get_company_info_service

router = APIRouter(
    prefix="/vacancies",
    tags=["Vacancies"],
)


@router.post(
    "",
    response_model=VacancyRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_vacancy(
    data: VacancyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_vacancy_service(
        db=db,
        data=data,
        owner_id=current_user.id,
    )


@router.get(
    "",
    response_model=VacancyList,
)
async def get_vacancies(
    search: str | None = None,
    company: str | None = None,
    location: str | None = None,
    work_format: str | None = None,
    salary_from: int | None = Query(
        default=None,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_vacancies_service(
        db=db,
        owner_id=current_user.id,
        search=search,
        company=company,
        location=location,
        work_format=work_format,
        salary_from=salary_from,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{vacancy_id}",
    response_model=VacancyRead,
)
async def get_vacancy(
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_vacancy_service(
        db=db,
        vacancy_id=vacancy_id,
        owner_id=current_user.id,
    )


@router.patch(
    "/{vacancy_id}",
    response_model=VacancyRead,
)
async def update_vacancy(
    vacancy_id: int,
    data: VacancyUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await update_vacancy_service(
        db=db,
        vacancy_id=vacancy_id,
        data=data,
        owner_id=current_user.id,
    )


@router.delete(
    "/{vacancy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_vacancy(
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await delete_vacancy_service(
        db=db,
        vacancy_id=vacancy_id,
        owner_id=current_user.id,
    )

@router.post(
    "/{vacancy_id}/analyze",
    response_model=JobQueued,
    status_code=status.HTTP_202_ACCEPTED,
)
async def analyze_vacancy(
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    vacancy = await get_vacancy_service(
        db=db,
        vacancy_id=vacancy_id,
        owner_id=current_user.id,
    )

    redis = await create_redis_pool()

    try:
        job = await redis.enqueue_job(
            "analyze_vacancy",
            vacancy.id,
        )

        if job is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Job was not queued",
            )

        return {
            "job_id": job.job_id,
            "status": "queued",
        }
    finally:
        await redis.aclose()


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
)
async def get_job_status(job_id: str):
    redis = await create_redis_pool()

    try:
        job = Job(
            job_id=job_id,
            redis=redis,
        )

        job_status = await job.status()
        status_value = job_status.value

        result = None

        if status_value == "complete":
            result = await job.result()

        return {
            "job_id": job_id,
            "status": status_value,
            "result": result,
        }
    finally:
        await redis.aclose()

@router.get(
    "/{vacancy_id}/company-info",
)
async def get_company_info(
    vacancy_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await get_company_info_service(
        db=db,
        vacancy_id=vacancy_id,
        owner_id=current_user.id,
    )
