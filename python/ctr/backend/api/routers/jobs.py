from fastapi import APIRouter, HTTPException

from backend.schemas.jobs import JobRequest, JobResponse
from backend.services import job_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

@router.post("/trigger", response_model=JobResponse)
async def trigger_job(request: JobRequest) -> JobResponse:
    try:
        return job_service.trigger_job(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
