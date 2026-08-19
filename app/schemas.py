from pydantic import BaseModel

class Instruction(BaseModel):
    sender: str
    receiver: str
    task: str


class VerifyRequest(BaseModel):
    instruction: Instruction
    signature: str
    token: str