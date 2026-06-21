from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any
import sqlite3

app = FastAPI(title="Heuristic Core Ingestion Engine", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 💾 DATABASE PERSISTENCE SETUP
def init_db():
    conn = sqlite3.connect('heuristic.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ledger 
                 (token TEXT PRIMARY KEY, client TEXT, tier TEXT, cost_per_packet REAL, total_billed REAL, credit_limit REAL)''')
    c.execute("INSERT OR IGNORE INTO ledger VALUES ('h_alpha_dev_882', 'Alpha Corporate Node', 'Pay-As-You-Go', 0.0050, 12.45, 20.00)")
    c.execute("INSERT OR IGNORE INTO ledger VALUES ('h_beta_enterprise_771', 'Beta Global Cluster', 'Enterprise High-Throughput', 0.0015, 489.10, 500.00)")
    conn.commit()
    conn.close()

init_db()

# 🧠 COGNITIVE "EYES" CLASSIFICATION
def classify_text(text: str):
    text = text.upper()
    if "CRITICAL" in text:
        return "HIGH_PRIORITY_ACTION"
    elif "PAYMENT" in text:
        return "FINANCIAL_TRANSACTION"
    else:
        return "GENERAL_DATA"

def perform_action(intent: str, content: str):
    if intent == "HIGH_PRIORITY_ACTION":
        return "✅ ACTION EXECUTED: Emergency Protocol Triggered"
    elif intent == "FINANCIAL_TRANSACTION":
        return "✅ ACTION EXECUTED: Ledger Settlement Initiated"
    else:
        return "ℹ️ NO ACTION REQUIRED"

API_KEY_NAME = "X-Heuristic-Token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

class IngestionPayload(BaseModel):
    payload_data: Any 

# 🚀 INGESTION ENGINE WITH PROFESSIONAL DOCUMENTATION
@app.post("/api/v1/ingest", status_code=status.HTTP_200_OK, tags=["Ingestion"])
async def ingest_unstructured_stream(payload: IngestionPayload, token: str = Security(api_key_header)):
    """
    Ingests unstructured data, performs classification, and settles against the persistent ledger.
    """
    conn = sqlite3.connect('heuristic.db')
    c = conn.cursor()
    c.execute("SELECT * FROM ledger WHERE token=?", (token,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied.")
    
    cost_per_packet = row[3]
    current_balance = row[4]
    credit_limit = row[5]
    
    # 🚨 HARD ENFORCEMENT GATE
    if current_balance >= credit_limit:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED, 
            detail={"error": "Insufficient funds", "message": "Credit limit reached. Please top up your account."}
        )
    
    new_balance = current_balance + cost_per_packet
    c.execute("UPDATE ledger SET total_billed=? WHERE token=?", (new_balance, token))
    conn.commit()
    conn.close()
    
    raw_data = payload.payload_data
    intent = classify_text(raw_data) if isinstance(raw_data, str) else "GENERAL_DATA"
    action_result = perform_action(intent, raw_data) if isinstance(raw_data, str) else "NONE"
        
    return {
        "status": "SUCCESS",
        "intent": intent,
        "action_result": action_result,
        "updated_ledger_balance": round(new_balance, 4),
        "credit_limit": credit_limit
    }