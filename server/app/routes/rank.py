"""Ranking/leaderboard routes."""

import json

from flask import Blueprint, request

from app.models.rank import get_rank_data, update_rank_data, find_user_rank
from app.models.user import get_uid_by_username
from app.utils.helpers import get_user_from_cookies

rank_bp = Blueprint("rank", __name__)


@rank_bp.route("/_4399/submit", methods=["POST", "GET"])
def submit_score():
    """Submit a score to the leaderboard."""
    user = get_user_from_cookies()
    local = json.loads(request.form.get("data", "[]"))
    if not local:
        return json.dumps({})

    entry = local[0]
    rid = str(entry.get("rId", "1501"))
    idx = int(request.form.get("idx", 0))

    new_score = {
        "id": user["uid"],
        "rId": int(rid),
        "gameid": "100027788",
        "index": idx,
        "uId": user["uid"],
        "userName": user["username"],
        "score": entry.get("score", 0),
        "rank": 1,
        "area": "中国",
        "extra": entry.get("extra", ""),
    }

    # Get existing rankings and update
    data = get_rank_data(int(rid))
    # Remove old entry for same user+index
    data = [item for item in data
            if not (str(item.get("uId")) == str(user["uid"])
                    and item.get("index") == idx)]
    data.append(new_score)
    update_rank_data(int(rid), data)

    # Re-read to get actual rank
    updated = get_rank_data(int(rid))
    rank = "1"
    score = str(new_score["score"])
    for item in updated:
        if str(item.get("uId")) == str(user["uid"]) and item.get("index") == idx:
            rank = str(item.get("rank", 1))
            score = str(item.get("score", 0))
            break

    response = {
        rid: {
            "code": "10000",
            "message": "1",
            "data": {
                "rank": rank,
                "rankLast": rank,
                "score": score,
                "scoreLast": score,
            },
        }
    }
    return json.dumps(response, ensure_ascii=False)


@rank_bp.route("/_4399/getRankingByPage", methods=["POST", "GET"])
def get_ranking_page():
    """Get paginated leaderboard data."""
    rank_id = int(request.form.get("rankId", 1501))
    page = int(request.form.get("page", 1))
    limit = int(request.form.get("limit", 10))

    data = get_rank_data(rank_id)
    start = (page - 1) * limit
    end = min(start + limit, len(data))

    result = {"code": "10000", "message": "1", "data": []}
    if start < len(data):
        result["data"] = data[start:end]

    return result


@rank_bp.route("/_4399/getRank", methods=["POST", "GET"])
def get_rank():
    """Get a specific user's rank."""
    rank_list_id = int(request.form.get("rankListId", 1501))
    uname = request.form.get("uname", "")

    uid = get_uid_by_username(uname)
    if not uid:
        return [{}]

    entry = find_user_rank(rank_list_id, uid)
    if entry:
        return {
            "code": "10000",
            "message": "1",
            "data": [entry],
        }

    return [{}]
