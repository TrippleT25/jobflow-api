from pydantic import BaseModel


class JobQueued(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: dict | None = None