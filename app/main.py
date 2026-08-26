from fastapi import FastAPI

from app.exceptions import unexpected_exception_handler
from app.logging_config import setup_logging
from app.middleware import LoggingMiddleware, RequestIDMiddleware
from app.routers.applications import router as applications_router
from app.routers.vacancies import router as vacancies_router
from app.routers.auth import router as auth_router

setup_logging()


app = FastAPI(
    title="JobFlow API",
    description=(
        "Backend service for managing "
        "vacancies and job applications."
    ),
    version="0.1.0",
)

app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

app.add_exception_handler(
    Exception,
    unexpected_exception_handler,
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(vacancies_router)
app.include_router(applications_router)
app.include_router(auth_router)