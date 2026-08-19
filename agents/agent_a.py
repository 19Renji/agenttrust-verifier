import json

from app.signature import sign_message
from app.jwt_utils import create_token

instruction = {
    "sender": "AgentA",
    "receiver": "AgentB",
    "task": "Summarize the quarterly sales report"
}

payload = {
    "instruction": instruction,
    "signature": sign_message(instruction),
    "token": create_token("AgentA", "AgentB")
}

print(json.dumps(payload, indent=2))