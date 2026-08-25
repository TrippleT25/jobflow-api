from sqlalchemy import func, or_, select
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
    search: str | None = None,
    company: str | None = None,
    location: str | None = None,
    work_format: str | None = None,
    salary_from: int | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Vacancy], int]:
    statement = select(Vacancy)

    if search:
        search_pattern = f"%{search}%"

        statement = statement.where(
            or_(
                Vacancy.title.ilike(search_pattern),
                Vacancy.company.ilike(search_pattern),
                Vacancy.description.ilike(search_pattern),
            )
        )

    if company:
        statement = statement.where(
            Vacancy.company.ilike(f"%{company}%")
        )

    if location:
        statement = statement.where(
            Vacancy.location.ilike(f"%{location}%")
        )

    if work_format:
        statement = statement.where(
            Vacancy.work_format == work_format
        )

    if salary_from is not None:
        statement = statement.where(
            Vacancy.salary_to >= salary_from
        )

    count_statement = select(
        func.count()
    ).select_from(
        statement.subquery()
    )

    total = await db.scalar(count_statement)

    statement = (
        statement
        .order_by(Vacancy.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.scalars(statement)

    return list(result.all()), total or 0


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
