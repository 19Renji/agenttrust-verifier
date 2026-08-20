from sqlalchemy.orm import Session


from app.models import AuditLog

def save_audit(db, sender, receiver, task, status, reason):
    log = AuditLog(
        sender=sender,
        receiver=receiver,
        task=task,
        status=status,
        reason=reason
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log