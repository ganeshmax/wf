import pandas as pd
import os
import json
from typing import Any

from backend.schemas.data import DatasetResponse, CTRFormsResponse, Form112, Form112Entity

def get_ctr_forms(limit: int = 100) -> CTRFormsResponse:
    path = "data/ctr/reports"
    if not os.path.exists(path):
        return CTRFormsResponse(data=[], total_rows=0, message="CTR Forms not found. Run CTR Generation first.")
        
    df = pd.read_parquet(path)
    df = df.fillna("")
    
    grouped = df.groupby("report_id")
    
    forms = []
    for report_id, group in grouped:
        direction = group.iloc[0]["direction"]
        date = group.iloc[0]["date"]
        report_amount = float(group.iloc[0]["report_amount"])
        status = group.iloc[0].get("status", "PENDING_REVIEW")
        
        entities = group[[
            "customer_id", "ctr_role", "entity_amount", "transaction_ids",
            "entity_type", "first_name", "last_name", "tin", "address", "city", "state", "zip"
        ]].to_dict('records')
        
        form_entities = []
        for ent in entities:
            # Parquet arrays become numpy NDArrays in pandas. Convert to list for Pydantic.
            ts_val = ent.get("transaction_ids", [])
            ent["transaction_ids"] = list(ts_val) if ts_val is not None else []
            form_entities.append(Form112Entity(**ent))
        sorted_entities = sorted(form_entities, key=lambda x: "Primary" not in x.ctr_role)
        
        forms.append(Form112(
            report_id=str(report_id),
            date=str(date),
            direction=direction,
            report_amount=report_amount,
            entity_count=len(entities),
            status=status,
            entities=sorted_entities
        ))
        
    forms = forms[:limit]
    return CTRFormsResponse(data=forms, total_rows=len(forms))

def get_dataset(dataset: str, limit: int = 100) -> tuple[dict[str, Any] | None, str | None]:
    valid_datasets = {
        "raw_customers": "data/raw/customers.csv",
        "raw_non_customers": "data/raw/non_customers.csv",
        "raw_locations": "data/raw/locations.csv",
        "raw_transactions": "data/raw/transactions.csv",
        "canonical_customers": "data/canonical/customers",
        "canonical_non_customers": "data/canonical/non_customers",
        "canonical_locations": "data/canonical/locations",
        "canonical_transactions": "data/canonical/transactions",
        "canonical_accounts": "data/canonical/accounts",
        "canonical_exemptions": "data/canonical/exemptions",
        "canonical_sars": "data/canonical/sars",
        "canonical_mils": "data/canonical/mils",
        "aggregated_ben_in": "data/aggregated/beneficiary_cash_in",
        "aggregated_ben_out": "data/aggregated/beneficiary_cash_out",
        "aggregated_cond_in": "data/aggregated/conductor_cash_in",
        "aggregated_cond_out": "data/aggregated/conductor_cash_out",
        "ctr": "data/ctr/reports",
        "ctr_stats": "data/ctr/stats.json"
    }
    
    if dataset not in valid_datasets:
        return None, "Dataset not found"
        
    path = valid_datasets[dataset]
    
    if not os.path.exists(path):
        return {"data": [], "total_rows": 0, "message": "Data not found. Run previous pipeline steps."}, None
        
    if path.endswith('.json'):
        with open(path, 'r') as f:
            return {"data": json.load(f)}, None
    elif path.endswith('.csv'):
        df = pd.read_csv(path)
    else:
        df = pd.read_parquet(path)
        
    df = df.fillna("")
    records = df.head(limit).to_dict(orient="records")
    return {"data": records, "total_rows": len(df)}, None

def get_transactions_by_ids(transaction_ids: list[str]) -> tuple[dict[str, Any] | None, str | None]:
    path = "data/canonical/transactions"
    if not os.path.exists(path):
        return None, "Canonical transactions not found."
    df = pd.read_parquet(path)
    df = df.fillna("")
    filtered = df[df["transaction_id"].isin(transaction_ids)]
    records = filtered.to_dict(orient="records")
    return {"data": records, "total_rows": len(records)}, None

def get_accounts_by_customer_ids(customer_ids: list[str]) -> tuple[dict[str, Any] | None, str | None]:
    path_owners = "data/canonical/account_owners"
    path_accounts = "data/canonical/accounts"
    
    if not os.path.exists(path_owners) or not os.path.exists(path_accounts):
        return None, "Canonical accounts data not found."
        
    owners_df = pd.read_parquet(path_owners)
    accounts_df = pd.read_parquet(path_accounts)
    
    owners_filtered = owners_df[owners_df["customer_id"].isin(customer_ids)]
    
    if owners_filtered.empty:
        return {"data": [], "total_rows": 0}, None
        
    merged = pd.merge(owners_filtered, accounts_df, on="account_id", how="left")
    merged = merged.fillna("")
    
    records = merged.to_dict(orient="records")
    return {"data": records, "total_rows": len(records)}, None

def update_ctr_form(report_id: str, updates: dict) -> Form112 | None:
    path = "data/ctr/reports"
    if not os.path.exists(path):
        return None
    
    df = pd.read_parquet(path)
    
    status = updates.get("status")
    entity_updates = updates.get("entities", [])
    
    mask = df["report_id"] == report_id
    if not mask.any():
        return None
        
    for ent in entity_updates:
        c_id = ent.get("customer_id")
        if not c_id: continue
        
        ent_mask = mask & (df["customer_id"] == c_id)
        
        if "tin" in ent and ent["tin"]:
            df.loc[ent_mask, "tin"] = ent["tin"]
        if "address" in ent and ent["address"]:
            df.loc[ent_mask, "address"] = ent["address"]
            
    if status:
        df.loc[mask, "status"] = status
        
    import shutil
    if os.path.isdir(path):
        shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    df.to_parquet(os.path.join(path, "part-updated.parquet"))
    
    forms_resp = get_ctr_forms(limit=5000)
    for form in forms_resp.data:
        if form.report_id == report_id:
            return form
    return None

def generate_fin_cen_xml(report_id: str) -> str | None:
    forms_resp = get_ctr_forms(limit=5000)
    target_form = None
    for form in forms_resp.data:
        if form.report_id == report_id:
            target_form = form
            break
            
    if not target_form:
        return None
        
    xml_parts = []
    xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_parts.append('<EFilingBatchXML>')
    xml_parts.append('  <FormTypeCode>112</FormTypeCode>')
    xml_parts.append('  <Activity>')
    xml_parts.append(f'    <EFilingActivityID>{target_form.report_id}</EFilingActivityID>')
    xml_parts.append(f'    <ActivityDate>{target_form.date}</ActivityDate>')
    xml_parts.append(f'    <TransactionDirection>{target_form.direction}</TransactionDirection>')
    xml_parts.append(f'    <TotalAmount>{target_form.report_amount}</TotalAmount>')
    
    for idx, ent in enumerate(target_form.entities):
        xml_parts.append('    <Party>')
        xml_parts.append(f'      <ActivityPartyTypeCode>{ent.ctr_role}</ActivityPartyTypeCode>')
        xml_parts.append('      <PartyName>')
        if ent.entity_type and ent.entity_type != "Individual":
            xml_parts.append(f'        <RawEntityName>{ent.first_name}</RawEntityName>')
        else:
            xml_parts.append(f'        <RawIndividualTitleName></RawIndividualTitleName>')
            xml_parts.append(f'        <RawEntityIndividualFirstName>{ent.first_name or ""}</RawEntityIndividualFirstName>')
            xml_parts.append(f'        <RawEntityIndividualLastName>{ent.last_name or ""}</RawEntityIndividualLastName>')
        xml_parts.append('      </PartyName>')
        xml_parts.append('      <Address>')
        xml_parts.append(f'        <RawStreetAddress1Text>{ent.address or ""}</RawStreetAddress1Text>')
        xml_parts.append(f'        <RawCityText>{ent.city or ""}</RawCityText>')
        xml_parts.append(f'        <RawStateCode>{ent.state or ""}</RawStateCode>')
        xml_parts.append(f'        <RawZIPCode>{ent.zip or ""}</RawZIPCode>')
        xml_parts.append('      </Address>')
        xml_parts.append('      <PartyIdentification>')
        xml_parts.append(f'        <PartyIdentificationNumberText>{ent.tin or ""}</PartyIdentificationNumberText>')
        xml_parts.append('      </PartyIdentification>')
        xml_parts.append(f'      <TotalEntityCashAmount>{ent.entity_amount}</TotalEntityCashAmount>')
        xml_parts.append('    </Party>')
        
    xml_parts.append('  </Activity>')
    xml_parts.append('</EFilingBatchXML>')
    return "\n".join(xml_parts)
