from pydantic import BaseModel
from typing import Any

class DatasetResponse(BaseModel):
    data: list[Any]
    total_rows: int = 0
    message: str | None = None

class Form112Entity(BaseModel):
    customer_id: str
    ctr_role: str
    entity_amount: float
    transaction_ids: list[str] = []
    entity_type: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    tin: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip: Any = None

class Form112(BaseModel):
    report_id: str
    date: str
    direction: str
    report_amount: float
    entity_count: int
    status: str = "PENDING_REVIEW"
    entities: list[Form112Entity]

class Form112UpdateRequest(BaseModel):
    entities: list[dict]
    status: str

class CTRFormsResponse(BaseModel):
    data: list[Form112]
    total_rows: int = 0
    message: str | None = None

class TransactionBatchRequest(BaseModel):
    transaction_ids: list[str]

class TransactionBatchResponse(BaseModel):
    data: list[Any]
    total_rows: int = 0
    message: str | None = None

class CustomerBatchRequest(BaseModel):
    customer_ids: list[str]

class AccountBatchResponse(BaseModel):
    data: list[Any]
    total_rows: int = 0
    message: str | None = None
