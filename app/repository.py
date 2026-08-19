from sqlalchemy.orm import Session
from app.models import AuditLog

def save_audit(db: Session, sender, receiver, task, status, reason):
    log = AuditLog(
        request_id=None,
        sender=sender,
        receiver=receiver,
        task=task,
        status=status,
        reason=reason
    )

    db.add(log)
    db.commit()