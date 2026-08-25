from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

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

    return await create_vacancy(
        db=db,
        data=data,
    )


async def get_vacancies_service(
    db: AsyncSession,
) -> list[Vacancy]:
    return await get_vacancies(db)


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

    return await update_vacancy(
        db=db,
        vacancy=vacancy,
        data=data,
    )


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