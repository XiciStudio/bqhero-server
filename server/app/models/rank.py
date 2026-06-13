"""Ranking/leaderboard database operations."""

import json
from app.extensions import query_one, query_all, execute


def get_rank_data(rank_id: int) -> list:
    """Get ranking entries for a specific rank ID."""
    row = query_one("SELECT data FROM top WHERE rid = ?", (rank_id,))
    return json.loads(row["data"]) if row else []


def update_rank_data(rank_id: int, data: list):
    """Update ranking entries, sorted by score descending."""
    sorted_data = sorted(data, key=lambda x: x.get("score", 0), reverse=True)
    for i, item in enumerate(sorted_data):
        item["rank"] = i + 1
    execute(
        "UPDATE top SET data = ? WHERE rid = ?",
        (json.dumps(sorted_data, ensure_ascii=False), rank_id),
    )


def find_user_rank(rank_id: int, uid: str) -> dict | None:
    """Find a user's rank entry."""
    data = get_rank_data(rank_id)
    for item in data:
        if str(item.get("uId")) == str(uid):
            return item
    return None
