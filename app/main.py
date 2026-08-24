from fastapi import FastAPI


app = FastAPI(
    title="JobFlow API",
    description="Backend service for managing vacancies and job applications.",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}