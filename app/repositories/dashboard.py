from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, ApplicationStatus
from app.models.vacancy import Vacancy


async def get_dashboard_stats(
    db: AsyncSession,
    owner_id: int,
):
    total_vacancies = await db.scalar(
        select(func.count(Vacancy.id)).where(
            Vacancy.owner_id == owner_id
        )
    )

    status_statement = (
        select(
            Application.status,
            func.count(Application.id),
        )
        .join(
            Vacancy,
            Application.vacancy_id == Vacancy.id,
        )
        .where(Vacancy.owner_id == owner_id)
        .group_by(Application.status)
    )

    result = await db.execute(status_statement)
    status_counts = {
        application_status: count
        for application_status, count in result.all()
    }
    by_status = {
        application_status: status_counts.get(
            application_status,
            0,
        )
        for application_status in ApplicationStatus
    }
    total_applications = sum(by_status.values())
    interviews = (
        by_status[ApplicationStatus.HR_SCREEN]
        + by_status[ApplicationStatus.TECH_INTERVIEW]
        + by_status[ApplicationStatus.FINAL_INTERVIEW]
    )

    return {
        "total_vacancies": total_vacancies or 0,
        "total_applications": total_applications,
        "offers": by_status[ApplicationStatus.OFFER],
        "rejections": by_status[ApplicationStatus.REJECTED],
        "interviews": interviews,
        "by_status": {
            application_status.value: count
            for application_status, count in by_status.items()
        },
    }
