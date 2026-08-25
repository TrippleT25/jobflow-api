from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VacancyCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    company: str = Field(min_length=1, max_length=255)

    url: str | None = None
    salary_from: int | None = Field(default=None, ge=0)
    salary_to: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=10)
    location: str | None = Field(default=None, max_length=255)
    work_format: str | None = Field(default=None, max_length=50)
    description: str | None = None


class VacancyUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    company: str | None = Field(default=None, min_length=1, max_length=255)

    url: str | None = None
    salary_from: int | None = Field(default=None, ge=0)
    salary_to: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=10)
    location: str | None = Field(default=None, max_length=255)
    work_format: str | None = Field(default=None, max_length=50)
    description: str | None = None


class VacancyRead(BaseModel):
    id: int
    title: str
    company: str

    url: str | None
    salary_from: int | None
    salary_to: int | None
    currency: str | None
    location: str | None
    work_format: str | None
    description: str | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VacancyList(BaseModel):
    items: list[VacancyRead]
    total: int
    limit: int
    offset: int
