"""Exchange code database operations."""

import uuid
from app.extensions import query_one, execute
from app.utils.crypto import encrypt_exchange_code


def get_code_by_id(code_id: str) -> dict | None:
    return query_one(
        "SELECT * FROM exchange_code WHERE id = ?", (code_id,)
    )


def create_code(code_type: str, num: int) -> str:
    """Create a new exchange code. Returns the encrypted code string."""
    code_id = str(uuid.uuid4().int)[0:6]
    execute(
        "INSERT INTO exchange_code (id, num, type, used) VALUES (?, ?, ?, ?)",
        (code_id, num, code_type, 0),
    )
    return encrypt_exchange_code(f"{code_id}&{num}&{code_type}&0")


def mark_code_used(code_id: str):
    execute(
        "UPDATE exchange_code SET used = 1 WHERE id = ?", (code_id,)
    )


def is_code_used(code_id: str) -> bool:
    row = query_one("SELECT used FROM exchange_code WHERE id = ?", (code_id,))
    if row:
        return bool(row["used"])
    return True  # non-existent codes treated as used
