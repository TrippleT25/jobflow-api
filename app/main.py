from fastapi import FastAPI

from app.routers.applications import router as applications_router
from app.routers.vacancies import router as vacancies_router

app = FastAPI(
    title="JobFlow API",
    description="Backend service for managing vacancies and job applications.",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(vacancies_router)
app.include_router(applications_router)