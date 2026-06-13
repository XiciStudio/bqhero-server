"""User database operations — all parameterized."""

import json
import uuid
from app.extensions import query_one, query_all, execute
from werkzeug.security import generate_password_hash, check_password_hash


def get_user_by_username(username: str) -> dict | None:
    return query_one("SELECT * FROM user WHERE username = ?", (username,))


def get_user_by_uid(uid: str) -> dict | None:
    return query_one("SELECT * FROM user WHERE uid = ?", (uid,))


def get_uid_by_username(username: str) -> str | None:
    row = query_one("SELECT uid FROM user WHERE username = ?", (username,))
    return row["uid"] if row else None


def create_user(username: str, password: str) -> str:
    """Create new user. Returns the assigned uid."""
    uid = str(uuid.uuid4().int)[0:6]
    hashed = generate_password_hash(password)
    execute(
        "INSERT INTO user (username, password, uid, data, Money, TotalRecharge) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (username, hashed, uid, "[]", 5000, 5000),
    )
    return uid


def verify_password(username: str, password: str) -> bool:
    """Check if password matches. Handles both hashed and legacy plaintext."""
    user = get_user_by_username(username)
    if not user:
        return False
    stored = user["password"]

    # Try bcrypt/werkzeug hash first
    try:
        if check_password_hash(stored, password):
            return True
    except Exception:
        pass

    # Legacy plaintext fallback (for existing data)
    if stored == password:
        # Upgrade to hashed
        upgrade_password(username, password)
        return True

    return False


def upgrade_password(username: str, password: str):
    """Upgrade plaintext password to hashed."""
    hashed = generate_password_hash(password)
    execute("UPDATE user SET password = ? WHERE username = ?", (hashed, username))


def check_user_exists(username: str) -> bool:
    row = query_one("SELECT 1 FROM user WHERE username = ?", (username,))
    return row is not None


# ---- Money operations ----

def get_money(username: str) -> int:
    row = query_one("SELECT Money FROM user WHERE username = ?", (username,))
    return row["Money"] if row else 0


def get_total_recharge(username: str) -> int:
    row = query_one("SELECT TotalRecharge FROM user WHERE username = ?", (username,))
    return row["TotalRecharge"] if row else 0


def add_money(username: str, amount: int) -> int:
    execute(
        "UPDATE user SET Money = Money + ?, TotalRecharge = TotalRecharge + ? WHERE username = ?",
        (amount, amount, username),
    )
    return get_money(username)


def deduct_money(username: str, amount: int) -> int:
    execute(
        "UPDATE user SET Money = Money - ? WHERE username = ?",
        (amount, username),
    )
    return get_money(username)


# ---- Save data operations ----

def get_save_metadata(username: str) -> str:
    """Get the 'data' JSON column (save slot metadata array)."""
    row = query_one("SELECT data FROM user WHERE username = ?", (username,))
    return row["data"] if row else "[]"


def update_save_metadata(username: str, data: str):
    execute("UPDATE user SET data = ? WHERE username = ?", (data, username))


def save_game_data(username: str, index: int, raw_data: str):
    """Store compressed game data in data_N column."""
    col = f"data_{index}"
    execute(
        f"UPDATE user SET `{col}` = ? WHERE username = ?",
        (raw_data, username),
    )


def get_game_data(username: str, index: int) -> str | None:
    """Get compressed game data from data_N column."""
    col = f"data_{index}"
    row = query_one(f"SELECT `{col}` FROM user WHERE username = ?", (username,))
    if row:
        return row[col]
    return None


# ---- Union membership ----

def set_union(username: str, union_id: int):
    execute("UPDATE user SET inunion_id = ? WHERE username = ?", (union_id, username))


def get_union_id(username: str) -> int | None:
    row = query_one("SELECT inunion_id FROM user WHERE username = ?", (username,))
    if row:
        return row["inunion_id"]
    return None


def set_union_by_uid(uid: str, union_id):
    execute("UPDATE user SET inunion_id = ? WHERE uid = ?", (union_id or 0, uid))
