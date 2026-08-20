from fastapi import FastAPI
from sqlalchemy import text
from app.database import Base, engine
from fastapi import Depends
from sqlalchemy.orm import Session
from app.jwt_utils import verify_token
from app.revocation import is_revoked
from app.database import get_db
from app.signature import verify_signature
from app.schemas import VerifyRequest
from app.repository import save_audit
from app.llm import execute_task
from app.logger import logger
import uuid
from app.signature import sign_message
from app.jwt_utils import create_token
from app.schemas import Instruction
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(
    title="AgentTrust Verifier",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",              # Local development
        "https://agenttrust-dashboard-theta.vercel.app"  # Your Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create tables automatically
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="AgentTrust Verifier",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "message": "AgentTrust API is running"
    }


@app.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
    "status": "healthy",
    "database": "connected",
    "llm": "configured",
    "version": "1.0.0"
}

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/verify")
def verify(request: VerifyRequest, db: Session = Depends(get_db)):
    instruction = request.instruction.model_dump()
    request_id = str(uuid.uuid4())
    if is_revoked(db, instruction["sender"]):
        save_audit(
            db,
            request_id,
            instruction["sender"],
            instruction["receiver"],
            instruction["task"],
            "Rejected",
            "Agent Revoked"
        )

        return {
            "status": "rejected",
            "reason": "Agent Revoked"
        }

    token_data = verify_token(request.token)

    if not token_data:
        save_audit(
            db,
            request_id,
            instruction["sender"],
            instruction["receiver"],
            instruction["task"],
            "Rejected",
            "Invalid Token"
        )

        return {
            "status": "rejected",
            "reason": "Invalid Token"
        }

    if not verify_signature(instruction, request.signature):
        save_audit(
            db,
            request_id,
            instruction["sender"],
            instruction["receiver"],
            instruction["task"],
            "Rejected",
            "Invalid Signature"
        )

        return {
            "status": "rejected",
            "reason": "Invalid Signature"
        }

    save_audit(
        db,
        request_id,
        instruction["sender"],
        instruction["receiver"],
        instruction["task"],
        "Accepted",
        "Verified"
    )
    logger.info(
    f"{instruction['sender']} verified successfully"
    )

    result = execute_task(instruction["task"])
    return {
    "status":"accepted",
    "llm_response":result
    }

from app.revocation import revoke_agent


@app.post("/revoke/{agent_name}")
def revoke(agent_name: str, db: Session = Depends(get_db)):
    revoke_agent(db, agent_name)

    return {
        "message": f"{agent_name} revoked successfully."
    }

from app.models import AuditLog

@app.get("/audit")
def audit(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).all()

    return [
        {
            "id": log.id,
            "sender": log.sender,
            "receiver": log.receiver,
            "task": log.task,
            "status": log.status,
            "reason": log.reason,
            "timestamp": log.timestamp
        }
        for log in logs
    ]

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "status":"error",
            "message":"Internal Server Error"
        }
    )

@app.post("/simulate/agent-a")
def simulate_agent_a(
    instruction: Instruction,
    tamper: bool = False,
    db: Session = Depends(get_db)
):
    original = instruction.model_dump()

    signature = sign_message(original)

    payload_instruction = original.copy()

    if tamper:
        payload_instruction["task"] = "Delete customer records"

    verify_request = VerifyRequest(
        instruction=payload_instruction,
        signature=signature,
        token=create_token("AgentA", "AgentB")
    )

    return verify(verify_request, db)

import os

@app.get("/debug/env")
def debug_env():
    return {
        "private_exists": bool(os.getenv("AGENTA_PRIVATE_KEY")),
        "public_exists": bool(os.getenv("AGENTA_PUBLIC_KEY")),
        "private_prefix": os.getenv("AGENTA_PRIVATE_KEY", "")[:30],
        "public_prefix": os.getenv("AGENTA_PUBLIC_KEY", "")[:30],
    }