from pydantic import BaseModel

class JobRequest(BaseModel):
    job_name: str

class JobResponse(BaseModel):
    status: str
    job: str
    logs: str
