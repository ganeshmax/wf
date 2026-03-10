import subprocess
import os

from backend.schemas.jobs import JobRequest, JobResponse

def trigger_job(request: JobRequest) -> JobResponse:
    jobs = {
        "ingestion": ["python", "data_pipelines/ingestion.py"],
        "aggregation": ["python", "data_pipelines/aggregation.py"],
        "ctr": ["python", "data_pipelines/ctr_generation.py"]
    }
    
    if request.job_name not in jobs:
        raise ValueError("Invalid job name")
        
    try:
        env = os.environ.copy()
        
        sdk_init = "source $HOME/.sdkman/bin/sdkman-init.sh && sdk use java 17.0.12-graal && "
        python_cmd = " ".join(jobs[request.job_name])
        
        full_command = f"{sdk_init}{python_cmd}"
        
        result = subprocess.run(
            full_command, 
            shell=True,
            executable='/bin/bash',
            capture_output=True, 
            text=True, 
            check=True,
            env=env
        )
        return JobResponse(status="success", job=request.job_name, logs=result.stdout)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Job failed: {e.stderr}")
