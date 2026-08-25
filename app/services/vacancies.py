from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import delete_cache_pattern, get_cache, set_cache
from app.models.vacancy import Vacancy
from app.repositories.vacancies import (
    create_vacancy,
    delete_vacancy,
    get_vacancies,
    get_vacancy_by_id,
    update_vacancy,
)
from app.schemas.vacancy import (
    VacancyCreate,
    VacancyUpdate,
)


async def create_vacancy_service(
    db: AsyncSession,
    data: VacancyCreate,
) -> Vacancy:
    if (
        data.salary_from is not None
        and data.salary_to is not None
        and data.salary_from > data.salary_to
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="salary_from cannot be greater than salary_to",
        )

    vacancy = await create_vacancy(
        db=db,
        data=data,
    )

    await delete_cache_pattern("vacancies:*")

    return vacancy


async def get_vacancies_service(
    db: AsyncSession,
    search: str | None = None,
    company: str | None = None,
    location: str | None = None,
    work_format: str | None = None,
    salary_from: int | None = None,
    limit: int = 20,
    offset: int = 0,
):
    cache_key = (
        "vacancies:"
        f"search={search}:"
        f"company={company}:"
        f"location={location}:"
        f"work_format={work_format}:"
        f"salary_from={salary_from}:"
        f"limit={limit}:"
        f"offset={offset}"
    )

    cached = await get_cache(cache_key)

    if cached is not None:
        return cached

    items, total = await get_vacancies(
        db=db,
        search=search,
        company=company,
        location=location,
        work_format=work_format,
        salary_from=salary_from,
        limit=limit,
        offset=offset,
    )

    result = {
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "company": item.company,
                "url": item.url,
                "salary_from": item.salary_from,
                "salary_to": item.salary_to,
                "currency": item.currency,
                "location": item.location,
                "work_format": item.work_format,
                "description": item.description,
                "created_at": item.created_at.isoformat(),
            }
            for item in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }

    await set_cache(
        cache_key,
        result,
        expire=60,
    )

    return result


async def get_vacancy_service(
    db: AsyncSession,
    vacancy_id: int,
) -> Vacancy:
    vacancy = await get_vacancy_by_id(
        db=db,
        vacancy_id=vacancy_id,
    )

    if vacancy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vacancy not found",
        )

    return vacancy


async def update_vacancy_service(
    db: AsyncSession,
    vacancy_id: int,
    data: VacancyUpdate,
) -> Vacancy:
    vacancy = await get_vacancy_service(
        db=db,
        vacancy_id=vacancy_id,
    )

    salary_from = (
        data.salary_from
        if data.salary_from is not None
        else vacancy.salary_from
    )

    salary_to = (
        data.salary_to
        if data.salary_to is not None
        else vacancy.salary_to
    )

    if (
        salary_from is not None
        and salary_to is not None
        and salary_from > salary_to
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="salary_from cannot be greater than salary_to",
        )

    vacancy = await update_vacancy(
        db=db,
        vacancy=vacancy,
        data=data,
    )

    await delete_cache_pattern("vacancies:*")

    return vacancy


async def delete_vacancy_service(
    db: AsyncSession,
    vacancy_id: int,
) -> None:
    vacancy = await get_vacancy_service(
        db=db,
        vacancy_id=vacancy_id,
    )

    await delete_vacancy(
        db=db,
        vacancy=vacancy,
    )

    await delete_cache_pattern("vacancies:*")
