from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vacancy import Vacancy
from app.schemas.vacancy import VacancyCreate, VacancyUpdate


async def create_vacancy(
    db: AsyncSession,
    data: VacancyCreate,
) -> Vacancy:
    vacancy = Vacancy(
        **data.model_dump()
    )

    db.add(vacancy)

    await db.commit()
    await db.refresh(vacancy)

    return vacancy


async def get_vacancies(
    db: AsyncSession,
) -> list[Vacancy]:
    statement = (
        select(Vacancy)
        .order_by(Vacancy.created_at.desc())
    )

    result = await db.scalars(statement)

    return list(result.all())


async def get_vacancy_by_id(
    db: AsyncSession,
    vacancy_id: int,
) -> Vacancy | None:
    return await db.get(
        Vacancy,
        vacancy_id,
    )


async def update_vacancy(
    db: AsyncSession,
    vacancy: Vacancy,
    data: VacancyUpdate,
) -> Vacancy:
    update_data = data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            vacancy,
            field,
            value,
        )

    await db.commit()
    await db.refresh(vacancy)

    return vacancy


async def delete_vacancy(
    db: AsyncSession,
    vacancy: Vacancy,
) -> None:
    await db.delete(vacancy)
    await db.commit()