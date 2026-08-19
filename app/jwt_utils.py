from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.config import settings

ALGORITHM = "HS256"


def create_token(sender, receiver, scope="execute_task"):
    payload = {
        "iss": sender,
        "aud": receiver,
        "scope": scope,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }

    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def verify_token(token):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[ALGORITHM],
            audience="AgentB"
        )

        return payload

    except JWTError:
        return None