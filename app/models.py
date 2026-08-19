from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from app.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    public_key = Column(String)
    revoked = Column(Boolean, default=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    request_id = Column(String)
    sender = Column(String)
    receiver = Column(String)
    task = Column(String)
    status = Column(String)
    reason = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Revocation(Base):
    __tablename__ = "revocations"

    id = Column(Integer, primary_key=True)
    agent_name = Column(String)
    revoked_at = Column(DateTime, default=datetime.utcnow)


class Reputation(Base):
    __tablename__ = "reputation"

    id = Column(Integer, primary_key=True)
    agent_name = Column(String)
    score = Column(Integer, default=100)