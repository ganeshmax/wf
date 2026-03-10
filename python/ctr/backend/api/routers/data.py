from typing import Annotated, Any
from fastapi import APIRouter, HTTPException, Query

from backend.schemas.data import CTRFormsResponse, DatasetResponse, TransactionBatchRequest, TransactionBatchResponse, Form112UpdateRequest, Form112, CustomerBatchRequest, AccountBatchResponse
from backend.services import data_service

router = APIRouter(prefix="/api/data", tags=["data"])

@router.get("/ctr_forms", response_model=CTRFormsResponse)
async def get_ctr_forms(limit: Annotated[int, Query(ge=1, le=1000)] = 100) -> Any:
    try:
        return data_service.get_ctr_forms(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/ctr_forms/{report_id}", response_model=Form112)
async def update_ctr_form(report_id: str, request: Form112UpdateRequest) -> Any:
    try:
        updated_form = data_service.update_ctr_form(report_id, request.dict())
        if not updated_form:
            raise HTTPException(status_code=404, detail="Form not found")
        return updated_form
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ctr_forms/{report_id}/xml")
async def get_ctr_form_xml(report_id: str) -> Any:
    try:
        xml_str = data_service.generate_fin_cen_xml(report_id)
        if not xml_str:
            raise HTTPException(status_code=404, detail="Form not found")
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(content=xml_str, media_type="application/xml")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{dataset}")
async def get_data(dataset: str, limit: Annotated[int, Query(ge=1, le=1000)] = 100) -> Any:
    try:
        data, error = data_service.get_dataset(dataset, limit)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/transactions/batch", response_model=TransactionBatchResponse)
async def get_transactions_batch(request: TransactionBatchRequest) -> Any:
    try:
        data, error = data_service.get_transactions_by_ids(request.transaction_ids)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accounts/batch", response_model=AccountBatchResponse)
async def get_accounts_batch(request: CustomerBatchRequest) -> Any:
    try:
        data, error = data_service.get_accounts_by_customer_ids(request.customer_ids)
        if error:
            raise HTTPException(status_code=404, detail=error)
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
