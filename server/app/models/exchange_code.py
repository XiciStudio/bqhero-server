"""Exchange code database operations."""

import uuid
from app.extensions import query_one, query_all, execute
from app.utils.crypto import encrypt_exchange_code


def get_code_by_id(code_id: str) -> dict | None:
    return query_one(
        "SELECT * FROM exchange_code WHERE id = ?", (code_id,)
    )


def create_code(code_type: str, num: int) -> str:
    """Create a new exchange code. Returns the encrypted code string."""
    code_id = str(uuid.uuid4().int)[0:6]
    encrypted = encrypt_exchange_code(f"{code_id}&{num}&{code_type}&0")
    execute(
        "INSERT INTO exchange_code (id, num, type, used, encrypted_code) VALUES (?, ?, ?, ?, ?)",
        (code_id, num, code_type, 0, encrypted),
    )
    return encrypted


def mark_code_used(code_id: str, username: str = None):
    execute(
        "UPDATE exchange_code SET used = 1, used_by = ?, used_at = datetime('now','localtime') WHERE id = ?",
        (username, code_id),
    )


def is_code_used(code_id: str) -> bool:
    row = query_one("SELECT used FROM exchange_code WHERE id = ?", (code_id,))
    if row:
        return bool(row["used"])
    return True  # non-existent codes treated as used


def get_all_codes(page: int = 1, per_page: int = 20) -> tuple:
    """Returns (codes_list, total_count) for paginated listing."""
    offset = (page - 1) * per_page
    total = query_one("SELECT COUNT(*) as cnt FROM exchange_code")
    total = total["cnt"] if total else 0
    rows = query_all(
        "SELECT * FROM exchange_code ORDER BY rowid DESC LIMIT ? OFFSET ?",
        (per_page, offset),
    )
    return rows, total


def get_code_count() -> int:
    row = query_one("SELECT COUNT(*) as cnt FROM exchange_code")
    return row["cnt"] if row else 0


def get_recent_redemptions(username: str, limit: int = 5) -> list:
    """Get recent code redemptions by a user."""
    return query_all(
        "SELECT num, type, used_at FROM exchange_code "
        "WHERE used_by = ? AND used = 1 "
        "ORDER BY used_at DESC LIMIT ?",
        (username, limit),
    )
