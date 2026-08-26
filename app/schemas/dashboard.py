from pydantic import BaseModel


class ApplicationStatusStats(BaseModel):
    NEW: int
    APPLIED: int
    HR_SCREEN: int
    TECH_INTERVIEW: int
    FINAL_INTERVIEW: int
    OFFER: int
    REJECTED: int


class DashboardStats(BaseModel):
    total_vacancies: int
    total_applications: int
    offers: int
    rejections: int
    interviews: int
    by_status: ApplicationStatusStats
