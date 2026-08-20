import os
import json
import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

PRIVATE_KEY_PATH = "keys/agentA_private.pem"
PUBLIC_KEY_PATH = "keys/agentA_public.pem"


def load_private_key():
    key = os.getenv("AGENTA_PRIVATE_KEY")

    if key:
        return serialization.load_pem_private_key(
            key.encode(),
            password=None
        )

    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )


def load_public_key():
    key = os.getenv("AGENTA_PUBLIC_KEY")

    if key:
        return serialization.load_pem_public_key(
            key.encode()
        )

    with open(PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(
            f.read()
        )


def sign_message(message):
    private_key = load_private_key()

    data = json.dumps(message, sort_keys=True).encode()

    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return base64.b64encode(signature).decode()


def verify_signature(message, signature):
    public_key = load_public_key()

    data = json.dumps(message, sort_keys=True).encode()

    try:
        public_key.verify(
            base64.b64decode(signature),
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )

        return True

    except Exception:
        return False