"""Union/guild database operations."""

import json
from app.extensions import query_one, query_all, execute


def get_all_unions() -> list:
    rows = query_all("SELECT info FROM union_data")
    return [json.loads(r["info"]) for r in rows]


def get_union_by_id(union_id: int) -> dict | None:
    row = query_one(
        "SELECT * FROM union_data WHERE id = ?", (union_id,)
    )
    if not row:
        return None
    return {
        "id": row["id"],
        "info": json.loads(row["info"]),
        "application": json.loads(row["application"]),
        "building": json.loads(row["building"]),
        "hegemony": json.loads(row["hegemony"]),
        "member": json.loads(row["member"]),
    }


def create_union(union_id: int, info: dict):
    execute(
        "INSERT INTO union_data (id, info, application, building, hegemony, member) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            union_id,
            json.dumps(info, ensure_ascii=False),
            "[]",
            "[]",
            "[]",
            json.dumps([], ensure_ascii=False),
        ),
    )


def update_union_info(union_id: int, info: dict):
    execute(
        "UPDATE union_data SET info = ? WHERE id = ?",
        (json.dumps(info, ensure_ascii=False), union_id),
    )


def update_union_members(union_id: int, members: list):
    execute(
        "UPDATE union_data SET member = ? WHERE id = ?",
        (json.dumps(members, ensure_ascii=False), union_id),
    )


def update_union_applications(union_id: int, apps: list):
    execute(
        "UPDATE union_data SET application = ? WHERE id = ?",
        (json.dumps(apps, ensure_ascii=False), union_id),
    )


def get_union_members(union_id: int) -> list:
    row = query_one(
        "SELECT member FROM union_data WHERE id = ?", (union_id,)
    )
    return json.loads(row["member"]) if row else []


def get_union_applications(union_id: int) -> list:
    row = query_one(
        "SELECT application FROM union_data WHERE id = ?", (union_id,)
    )
    return json.loads(row["application"]) if row else []
