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

app = FastAPI(
    title="AgentTrust Verifier",
    version="1.0.0"
)

# Create tables automatically
Base.metadata.create_all(bind=engine)


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
            "llm": "pending"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.post("/verify")
def verify(request: VerifyRequest, db: Session = Depends(get_db)):
    instruction = request.instruction.model_dump()

    if is_revoked(db, instruction["sender"]):
        save_audit(
            db,
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
        instruction["sender"],
        instruction["receiver"],
        instruction["task"],
        "Accepted",
        "Verified"
    )
    logger.info(
    f"{instruction['sender']} verified successfully"
)
    logger.warning(
    f"{instruction['sender']} failed verification"
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

    return logs

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